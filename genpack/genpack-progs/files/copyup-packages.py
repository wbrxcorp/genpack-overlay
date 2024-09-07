#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys,re,argparse,time,subprocess,logging,glob,shutil
import portage,portage.versions
from portage.dbapi import vartree

# /usr/lib/genpack/packages-and-sets

dry_run = False
path_prefix = "/"

vt = vartree.vartree()
api = vartree.vardbapi()

def get_masked_packages() -> set:
    masked_packages = set()
    genpack_mask_file = "/etc/portage/genpack.mask"
    if not os.path.isfile(genpack_mask_file): return masked_packages
    with open(genpack_mask_file) as f:
        for line in f:
            line = re.sub(r'#.*', "", line).strip()
            if line == "": continue
            #else
            masked_packages.add(line)
    return masked_packages

def get_package_set(set_name):
    pkgs = []
    with open(os.path.join("/etc/portage/sets", set_name)) as f:
        for line in f:
            line = re.sub(r'#.*', "", line).strip()
            if line != "": pkgs.append(line)
    return pkgs

def parse_depend(str):
    if str is None or str == "": return []
    reduced = portage.dep.use_reduce(str)
    pkgs = []
    idx = 0
    while idx < len(reduced):
        item = reduced[idx]
        if item[0] == "!":
            idx += 1
            continue
        #else
        if item == "||":
            candidates = reduced[idx+1]
            for candidate in candidates:
                if vt.dep_bestmatch(candidate) != "":
                    pkgs.append(candidate)
                    break
            idx += 2
            continue
        #else
        pkgs.append(item)
        idx += 1

    return pkgs

def scan_pkg(pkgnames, masked_packages, pkgs = None, needed_by = None, optional = False):
    if pkgs is None: pkgs = dict()
    for pkgname in pkgnames:
        if pkgname[0] == '@':
            if pkgname not in pkgs:
                pkgs[pkgname] = dict()
            if needed_by is not None:
                if "NEEDED_BY" not in pkgs[pkgname]: pkgs[pkgname]["NEEDED_BY"] = []
                pkgs[pkgname]["NEEDED_BY"].append(needed_by)
            scan_pkg(get_package_set(pkgname[1:]), masked_packages, pkgs, pkgname)
            continue
        #else
        bestmatch = vt.dep_bestmatch(pkgname)
        if bestmatch == "": raise Exception("no match for " + pkgname)
        if optional and portage.versions.pkgsplit(bestmatch)[0] in masked_packages: continue
        #else
        if bestmatch in pkgs:
            if needed_by is not None:
                if "NEEDED_BY" not in pkgs[bestmatch]: pkgs[bestmatch]["NEEDED_BY"] = []
                pkgs[bestmatch]["NEEDED_BY"].append(needed_by)
                continue
        #else:
        rdepend, pdepend, slot, inherited, description, use, homepage, license = api.aux_get(bestmatch, ["RDEPEND", "PDEPEND","SLOT", "INHERITED", "DESCRIPTION", "USE", "HOMEPAGE", "LICENSE"])

        # ignore packages with specific inherits
        if re.search(rf"(?<!\w)genpack-ignore(?!\w)", inherited) is not None:
            continue

        pkg = dict()
        pkgs[bestmatch] = pkg

        if needed_by is not None:
            if "NEEDED_BY" not in pkg: pkg["NEEDED_BY"] = []
            pkg["NEEDED_BY"].append(needed_by)
        
        if slot != "": pkg["SLOT"] = slot.replace("\n", " ")
        if inherited != "": pkg["INHERITED"] = inherited.replace("\n", " ")
        if description != "": pkg["DESCRIPTION"] = description.replace("\n", " ")
        if use != "": pkg["USE"] = use.replace("\n", " ")
        if homepage != "": pkg["HOMEPAGE"] = homepage.replace("\n", " ")
        if license != "": pkg["LICENSE"] = license.replace("\n", " ")

        for depend in [rdepend,pdepend]:
            scan_pkg(parse_depend(depend), masked_packages, pkgs, bestmatch, depend is pdepend)

    return pkgs

def touch(file):
    if dry_run:
        print(f"touch {file}")
        return
    #else
    logging.debug(f"Touching {file}")
    os.utime(file, (time.time(), os.lstat(file).st_mtime), follow_symlinks=False)

def is_path_excluded(path, devel = False):
    exclude_patterns = ["/run/","/var/run/","/var/lock/","/var/cache/","/usr/src/linux", "/usr/lib/genpack/"]
    if not devel: exclude_patterns += ["/usr/share/man/","/usr/share/doc/","/usr/share/gtk-doc/","/usr/share/info/",
        "/usr/include/",re.compile(r'^/usr/lib/python[0-9\.]+?/test/'),re.compile(r'\.a$')]
    for expr in exclude_patterns:
        if isinstance(expr, re.Pattern):
            if re.search(expr, path): return True
        elif isinstance(expr, str):
            if path.startswith(expr): return True
        else:
            raise Exception("Unknown type")
    return False

def touch_all_files_of_all_packages(pkgs, devel):
    logging.debug(f"Touching all files of packages {pkgs}")
    for pkg in pkgs:
        if pkg[0] == '@': continue
        contents_file = os.path.join("/var/db/pkg" , pkg, "CONTENTS")
        if not os.path.isfile(contents_file): continue
        #else
        with open(contents_file) as f:
            while line := f.readline():
                line = re.sub(r'#.*$', "", line).strip()
                if line == "": continue
                file_to_append = None
                if line.startswith("obj "): 
                    file_to_append = re.sub(r' [0-9a-f]+ [0-9]+$', "", line[4:])
                    if not os.path.exists(file_to_append):
                        print(f"# file {file_to_append} does not exist", file=sys.stderr)
                        file_to_append = None
                elif line.startswith("sym "):
                    file_to_append = re.sub(r' -> .+$', "", line[4:])
                    if not os.path.islink(file_to_append):
                        print(f"# link {file_to_append} does not exist", file=sys.stderr)
                        file_to_append = None
                if file_to_append is not None and not is_path_excluded(file_to_append, devel):
                    touch(os.path.join(path_prefix, file_to_append.lstrip("/")))

def copyup_toplevel_dirs():
    for dir in ["bin", "sbin", "lib", "lib64", "usr/sbin", "run", "dev", "proc", "sys", "root", "home", "tmp", "var/run", "mnt"]:
        logging.debug(f"Touching {dir} if it exists")
        d = os.path.join(path_prefix, dir)
        if os.path.lexists(d): touch(d)

def generate_metadata(pkgs_with_deps):
    genpack_metadata_dir = "/.genpack"
    os.makedirs(genpack_metadata_dir, exist_ok=True)
    
    with open(os.path.join(genpack_metadata_dir, "arch"), "w") as f:
        f.write(os.uname().machine)
    if "PROFILE" in os.environ:
        with open(os.path.join(genpack_metadata_dir, "profile"), "w") as f:
            f.write(os.environ["PROFILE"])
    if "ARTIFACT" in os.environ:
        with open(os.path.join(genpack_metadata_dir, "artifact"), "w") as f:
            f.write(os.environ["ARTIFACT"])
    if "VARIANT" in os.environ:
        with open(os.path.join(genpack_metadata_dir, "variant"), "w") as f:
            f.write(os.environ["VARIANT"])
    portage_dir = "/var/db/repos/gentoo"
    shutil.copy2(os.path.join(portage_dir, "metadata/timestamp.commit"), os.path.join(genpack_metadata_dir, "timestamp.commit"))
    with open(os.path.join(genpack_metadata_dir, "packages"), "w") as f:
        for pkgname, pkg in pkgs_with_deps.items():
            if pkgname[0] == '@': continue # skip package set
            #else
            f.write((("%s[%s]" % (pkgname, pkg["SLOT"])) if "SLOT" in pkg else pkgname) + '\n')
            if "NEEDED_BY" in pkg:
                f.write("# NEEDED_BY: " + (' '.join(pkg["NEEDED_BY"])) + '\n')
            pkg_properties = ["DESCRIPTION", "USE", "HOMEPAGE", "LICENSE"]
            for prop in pkg_properties:
                if prop in pkg:
                    f.write("# " + prop + ": " + pkg[prop] + '\n')
            f.write('\n')

def main(pkgs, bind_mount_root, toplevel_dirs, exec_package_scripts, devel, _generate_metadata):
    pkgs_with_deps = scan_pkg(pkgs, get_masked_packages())

    global path_prefix
    if bind_mount_root: 
        logging.debug("Bind mounting root directory to /run/mnt")
        os.makedirs("/run/mnt", exist_ok=True)
        subprocess.run(["mount", "--bind", "/", "/run/mnt"], check=True)
        path_prefix = "/run/mnt"
    try:
        if toplevel_dirs: copyup_toplevel_dirs()
        touch_all_files_of_all_packages(sorted(pkgs_with_deps.keys()), devel)
    finally:
        if bind_mount_root:
            logging.debug("Unmounting /run/mnt")
            subprocess.run(["umount", "/run/mnt"], check=True)
    if exec_package_scripts:
        for pkg in pkgs_with_deps.keys():
            if pkg[0] == '@': continue
            #else
            for f in sorted(glob.glob("/usr/lib/genpack/package-scripts/%s/*" % (portage.versions.pkgsplit(pkg)[0]))):
                if not os.access(f, os.X_OK): continue
                #else
                logging.info(f"Executing package script {f}")
                if not dry_run: subprocess.run([f], check=True)
    if _generate_metadata:
        generate_metadata(pkgs_with_deps)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy-up all packages')
    parser.add_argument("pkgs", type=str, nargs='+', help='List of packages')
    parser.add_argument("--bind-mount-root", action="store_true", help="Bind mount root directory")
    parser.add_argument("--toplevel-dirs", action="store_true", help="Copy-up top-level dirs like /run, /dev...")
    parser.add_argument("--exec-package-scripts", action="store_true", help="Execute package scripts")
    parser.add_argument("--devel", action="store_true", help="Copy-up devel files")
    parser.add_argument("--generate-metadata", action="store_true", help="Generate metadata under /.genpack")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--loglevel", type=str, default="INFO", help="Log level")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    if args.dry_run: dry_run = True
    main(args.pkgs, args.bind_mount_root, args.toplevel_dirs, 
         args.exec_package_scripts, args.devel, args.generate_metadata)
