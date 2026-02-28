#!/usr/bin/env python3
# A utility to determin rpm pacckage URL to download
# Usage: get-rpm-download-url.py <repo> <package> [--arch <arch>] [--ttl <ttl>]
# 
import argparse,os,time,pickle,urllib3,logging

CACHE_DIR = "/var/cache/get-rpm-download-url" if os.geteuid() == 0 else os.path.expanduser("~/.cache/get-rpm-download-url")

def determine_cache_path(repo):
    # use sha256 hash of repo as cache file name
    import hashlib
    m = hashlib.sha256()
    m.update(repo.encode())
    return os.path.join(CACHE_DIR, m.hexdigest())


def put_cache(repo, content):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = determine_cache_path(repo)
    with open(cache_path, "wb") as f:
        pickle.dump(content, f)

def get_cache(repo, ttl=3600):
    cache_path = determine_cache_path(repo)
    if os.path.exists(cache_path):
        if os.path.getmtime(cache_path) + ttl < time.time():
            os.unlink(cache_path)
            return None
    else:
        return None

    try:
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def download_primary_xml(repo):
    repomd_xml_url = repo + "repodata/repomd.xml"
    logging.debug("Downloading %s" % repomd_xml_url)
    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    r = http.request('GET', repomd_xml_url)
    if r.status != 200:
        raise Exception("Failed to download %s" % repomd_xml_url)
    # parse response body as XML
    from xml.etree import ElementTree
    root = ElementTree.fromstring(r.data)
    # find primary.xml.gz
    primary_xml_gz_url = None
    for data in root.findall("{http://linux.duke.edu/metadata/repo}data"):
        if data.get("type") == "primary":
            primary_xml_gz_url = repo + data.find("{http://linux.duke.edu/metadata/repo}location").get("href")
            break
    if primary_xml_gz_url is None:
        raise Exception("Failed to find primary.xml.gz in %s" % repomd_xml_url)
    # download primary.xml.gz
    r = http.request('GET', primary_xml_gz_url)
    if r.status != 200:
        raise Exception("Failed to download %s" % primary_xml_gz_url)
    # parse response body as XML
    decompression_func = None
    if primary_xml_gz_url.endswith(".gz"):
        import gzip
        decompression_func = gzip.decompress
    elif primary_xml_gz_url.endswith(".bz2"):
        import bz2
        decompression_func = bz2.decompress
    elif primary_xml_gz_url.endswith(".xz"):
        import lzma
        decompression_func = lzma.decompress
    else:
        raise Exception("Unknown compression format: %s" % primary_xml_gz_url)

    primary_xml = ElementTree.fromstring(decompression_func(r.data))

    packages = []

    for pkg in primary_xml.findall("{http://linux.duke.edu/metadata/common}package"):
        pkg_name = pkg.find("{http://linux.duke.edu/metadata/common}name").text
        pkg_arch = pkg.find("{http://linux.duke.edu/metadata/common}arch").text
        pkg_time = pkg.find("{http://linux.duke.edu/metadata/common}time").get("file")
        pkg_location = pkg.find("{http://linux.duke.edu/metadata/common}location").get("href")
        packages.append({
            "name":pkg_name,
            "arch":pkg_arch,
            "time":int(pkg_time),
            "location":pkg_location
        })
    return packages

def main(repo, package, arch, ttl=3600):
    packages = get_cache(repo, ttl)
    if packages is None:
        packages = download_primary_xml(repo)
        # save to cache
        put_cache(repo, packages)
    else:
        logging.debug("Using cache")

    # find package
    matched = None
    for pkg in packages:
        if pkg["name"] != package or pkg["arch"] not in ["noarch", arch]: continue
        if matched is None or pkg["time"] > matched["time"]:
            matched = pkg
    if matched is not None: print(repo + matched["location"])
    else: raise Exception("Package not found: %s" % package)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show RPM download URL for specified repository and package')
    parser.add_argument('repo', help='Repository URL contains "repodata" subdirectory')
    parser.add_argument('package', help='Package name')
    parser.add_argument("--arch", default= os.uname()[4], help="Architecture")
    parser.add_argument("--ttl", type=int, default=3600, help="Cache TTL in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug: logging.basicConfig(level=logging.DEBUG)

    repo = str(args.repo)

    main(repo if repo.endswith("/") else repo + '/', args.package, args.arch, args.ttl)
