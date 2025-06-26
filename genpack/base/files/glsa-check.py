#!/usr/bin/python3 -B

import os,argparse,re,glob,logging,tarfile,io,subprocess
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import portage.versions # /usr/lib/python*/site-packages/portage/versions.py

RSYNC_URLS = [
    ("rsync://ftp.riken.jp/gentoo-portage", True),
    ("rsync://ftp.jaist.ac.jp/pub/Linux/Gentoo-portage", False), 
    ("rsync://repo.jing.rocks/gentoo-portage", True)
]

def parse_package_line(line):
    logging.debug("Parsing package line: %s" % line)
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

    logging.debug("Parsed package and version: %s" % package_and_version)
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
    logging.debug("Checking %s" % version)
    for unv in unvs:
        if slot is not None and slot != unv[2]: continue
        #else
        if condition_matches(version, unv[1], unv[3]): return unv[0]
    return False

def check(packages_file, glsa_dir, mask_dir):
    logging.info("Checking GLSAs against installed packages from %s" % packages_file)

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
    return vulnerabilities

def sync(glsa_dir, rsync_url=None):
    rsync_urls = [(rsync_url, False)] if rsync_url else RSYNC_URLS
    success = False
    for url in rsync_urls:
        logging.info("Syncing GLSA data from %s" % url[0])
        try:
            rsync_cmdline =  ["rsync", "-a", "--delete", "--quiet"]
            if url[1]:  # If the URL allows compression
                rsync_cmdline.append("--compress")
            rsync_cmdline += [f"{url[0]}/metadata/glsa/", glsa_dir]
            subprocess.run(rsync_cmdline, check=True)
            success = True
            break
        except Exception as e:
            logging.error(f"Failed to sync from {url[0]}: {e}")
    if not success:
        raise Exception("Failed to sync GLSA data from all provided URLs.")
    #else
    logging.info("GLSA data synced successfully.")
    timestamp_commit = open("/var/lib/genpack/glsa-check/glsa/timestamp.commit").read().strip().split()
    if len(timestamp_commit) < 3:
        logging.warning("Timestamp commit file is malformed. using placeholder.")
        return "0000-00-00T00:00:00Z"
    #else
    return timestamp_commit[2]  # Return the timestamp from the commit file

def get_data_dir():
    return "/var/lib/genpack/glsa-check" if os.getuid() == 0 else os.path.expanduser("~/.local/lib/genpack/glsa-check")

if __name__ == '__main__':
    data_dir = get_data_dir()
    parser = argparse.ArgumentParser(description='GLSA Check')
    parser.add_argument("--debug", action='store_true', help="Enable debug logging")
    parser.add_argument("--packages-file", default="/.genpack/packages")
    parser.add_argument("--rsync-url", default=None, help="Rsync URL to sync GLSA data (default: use predefined URLs)")
    parser.add_argument("--data-dir", default=data_dir, help="Directory to store downloaded data")
    parser.add_argument("--check-even-if-unchanged", action='store_true', help="Check GLSAs even if the portage snapshot is unchanged")
    parser.add_argument("--outfile", default=os.path.join(data_dir,"glsa-check.out"), help="Output file to save the results")
    parser.add_argument("--remove-outfile-if-no-vulnerabilities", action='store_true', help="Remove the output file if no vulnerabilities are found")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    os.makedirs(args.data_dir, exist_ok=True)
    glsa_dir = os.path.join(args.data_dir, "glsa")

    glsa_timestamp = sync(glsa_dir, args.rsync_url)
    mask_dir = os.path.join(args.data_dir, "mask")
    vulnerabilities = check(args.packages_file, glsa_dir, mask_dir)

    current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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
                    f.write(f"# GLSA timestamp: {glsa_timestamp}\n")
                    f.write(f"# Check time: {current_timestamp}\n")
        exit(0)

    #else    
    logging.info("Vulnerabilities found:")
    f = open(args.outfile, "w") if args.outfile else None
    if f is not None:
        f.write("# Vulnerabilities found:\n")
        f.write(f"# packages file: {args.packages_file}\n")
        f.write(f"# GLSA timestamp: {glsa_timestamp}\n")
        f.write(f"# Check time: {current_timestamp}\n")
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
