#!/usr/bin/python3 -B

import os,argparse,re,glob,logging,tarfile,io
import xml.etree.ElementTree as ET

import requests
import portage.versions # /usr/lib/python*/site-packages/portage/versions.py

DEFAULT_PORTAGE_LATEST_URL = "http://ftp.iij.ad.jp/pub/linux/gentoo/snapshots/portage-latest.tar.xz"

def parse_package_line(line):
    #print(line)
    category, package_and_version_and_revision_and_slot = line.split('/', 1)

    slotpos = re.search(r'\[.*\]$', package_and_version_and_revision_and_slot)
    if slotpos:
        slot = package_and_version_and_revision_and_slot[slotpos.start() + 1:slotpos.end() - 1]
        package_and_version_and_revision = package_and_version_and_revision_and_slot[:slotpos.start()]
    else:
        slot = None
        package_and_version_and_revision = package_and_version_and_revision_and_slot

    revpos = re.search('-r\\d+$', package_and_version_and_revision)
    if revpos:
        revision = int(package_and_version_and_revision[revpos.start() + 2:])
        package_and_version = package_and_version_and_revision[:revpos.start()]
    else:
        revision = None
        package_and_version = package_and_version_and_revision
    
    #print(package_and_version)
    package, version = package_and_version.rsplit('-', 1)

    return [category, package, version, revision, slot]

def split_revision(line):
    revpos = re.search('-r\\d+$', line)
    if revpos:
        return [line[:revpos.start()], int(line[revpos.start() + 2:])]
    else:
        return [line, None]

def condition_matches(installed, range, specified):
    cmp = portage.versions.vercmp(installed, specified)
    if range == "ge":
        return  cmp >= 0
    elif range == "gt":
        return cmp > 0
    elif range == "le":
        return cmp <= 0
    elif range == "lt":
        return cmp < 0
    elif range == "eq":
        return cmp == 0        
    #else(rlt|rle|rgt|rgt)
    installed_v, installed_r = split_revision(installed)
    specified_v, specified_r = split_revision(specified)
    if installed_v != specified_v: return False
    #else
    if range == "rlt":
        return installed_r < specified_r
    elif range == "rle":
        return installed_r <= specified_r
    elif range == "rgt":
        return installed_r > specified_r
    elif range == "rge":
        return installed_r >= specified_r

    raise Exception("Unknown range: %s" % range)

def is_package_affected(version, slot, unvs):
    #print("Checking %s" % version)
    for unv in unvs:
        if slot is not None and slot != unv[2]: continue
        #else
        if condition_matches(version, unv[1], unv[3]): return unv[0]
    return False

def check(packages_file, glsa_dir, mask_dir):
    installed_packages = {}
    with open(packages_file) as f:
        while True:
            line = f.readline()
            if not line: break
            package = line.strip()
            if package.startswith('#') or package == "": continue
            if package.startswith('@') or package.startswith("virtual/"): continue
            category, package_name, version, revision, slot = parse_package_line(package)
            installed_packages[category + "/" + package_name] = [version + ("-r" + str(revision) if revision else ""), None] # slot is not known

    #vulnerability_found = False
    vulnerabilities = {}

    # read all GLSAs under portage_dir/metadata/glsa
    for glsa_file in sorted(glob.glob("*.xml", root_dir=glsa_dir)):
        root = ET.parse(os.path.join(glsa_dir, glsa_file)).getroot()
        glsa_id = root.attrib['id']
        if mask_dir is not None and os.path.exists(os.path.join(mask_dir, glsa_id)):
            logging.debug("GLSA %s is masked, skipping." % glsa_id)
            continue
        for affected in root.findall('affected'):
            for package in affected.findall('package'):
                package_name = package.attrib['name']
                if package_name not in installed_packages: continue
                #else
                unvs = []
                for unaffected_or_vulnerable in package:
                    if unaffected_or_vulnerable.tag not in ["unaffected", "vulnerable"]: continue
                    range = unaffected_or_vulnerable.attrib['range']
                    slot = unaffected_or_vulnerable.attrib.get('slot', None)
                    version = unaffected_or_vulnerable.text.strip()
                    unvs.append([unaffected_or_vulnerable.tag == "vulnerable", range, slot, version])
                version, slot = installed_packages[package_name]
                if is_package_affected(version, slot, unvs):
                    package_name_and_version = package_name + "-" + version
                    if package_name_and_version not in vulnerabilities:
                        vulnerabilities[package_name_and_version] = []
                    vulnerabilities[package_name_and_version].append(glsa_id)
                    #print("%s-%s is affected by https://security.gentoo.org/glsa/%s" % (package_name, version, glsa_id))
                    #vulnerability_found = True
    return vulnerabilities

def download(url, glsa_dir, last_headers = None):
    headers = {'User-Agent': "genpack-glsa-check/1.0"}
    response = requests.head(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    headers = f"Last-Modified:{response.headers.get('Last-Modified', '')} ETag:{response.headers.get('ETag', '')} Content-Length:{response.headers.get('Content-Length', '')}"

    if last_headers == headers and os.path.exists(glsa_dir):
        logging.info("Portage is unchanged since last check.")
        return None
    #else
    os.makedirs(glsa_dir, exist_ok=True)
    # download and extract
    logging.info("Downloading portage from %s" % url)
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an error for bad responses
    response.raw.decode_content = True

    stream = io.BufferedReader(response.raw)

    # ストリーミングモードで開く ("r|xz" または圧縮自動判別の "r|*")
    with tarfile.open(fileobj=stream, mode="r|xz") as tar:
        for member in tar:
            # ここで欲しいファイルだけを判定
            if not member.name.startswith("portage/metadata/glsa"): continue
            if not member.isfile(): continue
            #else
            target = os.path.join(glsa_dir, os.path.basename(member.name))
            f = tar.extractfile(member)
            if f is None: continue
            #else
            with open(target, "wb") as out:
                out.write(f.read())
            logging.debug("Extracted %s", member.name)

    logging.info("Portage downloaded and saved.")
    return headers

def get_data_dir():
    return "/var/lib/genpack/glsa-check" if os.getuid() == 0 else os.path.expanduser("~/.local/lib/genpack/glsa-check")

if __name__ == '__main__':
    data_dir = get_data_dir()
    parser = argparse.ArgumentParser(description='GLSA Check')
    parser.add_argument("--debug", action='store_true', help="Enable debug logging")
    parser.add_argument("--packages-file", default="/.genpack/packages")
    parser.add_argument("--portage-url", default=DEFAULT_PORTAGE_LATEST_URL, help="URL to download the latest portage snapshot")
    parser.add_argument("--data-dir", default=data_dir, help="Directory to store downloaded data")
    parser.add_argument("--check-even-if-unchanged", action='store_true', help="Check GLSAs even if the portage snapshot is unchanged")
    parser.add_argument("--outfile", default=os.path.join(data_dir,"glsa-check.out"), help="Output file to save the results")
    parser.add_argument("--remove-outfile-if-no-vulnerabilities", action='store_true', help="Remove the output file if no vulnerabilities are found")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    glsa_dir = os.path.join(args.data_dir, "glsa")
    last_headers_path = os.path.join(args.data_dir, "portage-headers")
    last_headers = open(last_headers_path, "r").read().strip() if os.path.exists(last_headers_path) else None
    headers = download(args.portage_url, glsa_dir, last_headers)
    if headers is None or headers == last_headers:
        logging.info("No new GLSAs found.")
        if not args.check_even_if_unchanged:
            exit(0)
    #else
    mask_dir = os.path.join(args.data_dir, "mask")
    vulnerabilities = check(args.packages_file, glsa_dir, mask_dir)
    if headers is not None:
        with open(last_headers_path, "w") as f:
            f.write(headers)

    if len(vulnerabilities) == 0:
        logging.info("No vulnerabilities found.")
        if args.outfile is not None:
            if args.remove_outfile_if_no_vulnerabilities:
                if os.path.exists(args.outfile):
                    os.remove(args.outfile)
                    logging.info("Removed output file %s as no vulnerabilities were found." % args.outfile)
            else:
                with open(args.outfile, "w") as f:
                    f.write("# No vulnerabilities found.\n")
                    f.write(f"# packages file: {args.packages_file}\n")
                    f.write(f"# portage headers: {headers or last_headers}\n")
        exit(0)

    #else    
    logging.info("Vulnerabilities found:")
    f = open(args.outfile, "w") if args.outfile else None
    if f is not None:
        f.write("# Vulnerabilities found:\n")
        f.write(f"# packages file: {args.packages_file}\n")
        f.write(f"# portage headers: {headers or last_headers}\n")
    for package, glsa_ids in vulnerabilities.items():
        logging.info("  %s: %s", package, ", ".join(glsa_ids))
        if f is not None: 
            f.write("%s: %s\n" % (package, ", ".join(glsa_ids)))
    if f is not None:
        f.close()
        logging.info("Results saved to %s" % args.outfile)
    os.makedirs(mask_dir, exist_ok=True)
    logging.info("Check every https://security.gentoo.org/glsa/YYYYMM-NN for more details(YYYYMM-NN is GLSA ID).")
    logging.info("You can mask GLSAs by creating a file named after the GLSA ID in %s." % mask_dir)
