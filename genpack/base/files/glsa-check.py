#!/usr/bin/python3 -B

import os,argparse,re,glob
import xml.etree.ElementTree as ET

import portage.versions # /usr/lib/python*/site-packages/portage/versions.py

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

def main(packages_file, glsa_dir):
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
    #for package in packages:
    #    print(package)

    # read all GLSAs under portage_dir/metadata/glsa
    for glsa_file in sorted(glob.glob("*.xml", root_dir=glsa_dir)):
        root = ET.parse(os.path.join(glsa_dir, glsa_file)).getroot()
        glsa_id = root.attrib['id']
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
                    print("%s-%s is affected by https://security.gentoo.org/glsa/%s" % (package_name, version, glsa_id))

if __name__ == '__main__':
    # mkdir -p /var/db/repos/gentoo
    # curl http://ftp.iij.ad.jp/pub/linux/gentoo/snapshots/portage-latest.tar.xz| tar Jxf - -C /var/db/repos/gentoo portage/metadata/glsa --strip-components=1
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GLSA Check')
    parser.add_argument('--packages-file', default="/.genpack/packages")
    parser.add_argument('--glsa-dir', default="/var/db/repos/gentoo/metadata/glsa")
    args = parser.parse_args()

    main(args.packages_file, args.glsa_dir)
