#!/usr/bin/python3 
import os,sys,re,argparse,logging,pickle
from pathlib import Path

import portage
from portage.dbapi import vartree

vt = vartree.vartree()
api = vartree.vardbapi()

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
    pkgs = set()
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
                    pkgs.add(candidate)
                    break
            idx += 2
            continue
        #else
        pkgs.add(item)
        idx += 1

    # return as list
    return list(pkgs)

def scan_pkg(pkgnames, dep_removals, pkgs = None, needed_by = None):
    if pkgs is None: pkgs = dict()
    for pkgname in pkgnames:
        if pkgname[0] == '@':
            if pkgname not in pkgs:
                pkgs[pkgname] = dict()
            if needed_by is not None:
                if "NEEDED_BY" not in pkgs[pkgname]: pkgs[pkgname]["NEEDED_BY"] = set()
                pkgs[pkgname]["NEEDED_BY"].add(needed_by)
            scan_pkg(get_package_set(pkgname[1:]), dep_removals, pkgs, pkgname)
            continue
        #else
        bestmatch = vt.dep_bestmatch(pkgname)
        if bestmatch == "": raise Exception("no match for " + pkgname)
        #else
        if bestmatch in pkgs:
            if needed_by is not None:
                if "NEEDED_BY" not in pkgs[bestmatch]: pkgs[bestmatch]["NEEDED_BY"] = set()
                pkgs[bestmatch]["NEEDED_BY"].add(needed_by)
                continue
        #else:
        rdepend, pdepend, slot, inherited, description, use, homepage, license = api.aux_get(bestmatch, ["RDEPEND", "PDEPEND","SLOT", "INHERITED", "DESCRIPTION", "USE", "HOMEPAGE", "LICENSE"])

        # ignore packages with specific inherits
        if re.search(rf"(?<!\w)genpack-ignore(?!\w)", inherited) is not None:
            continue

        pkg = dict()
        pkgs[bestmatch] = pkg

        if needed_by is not None:
            if "NEEDED_BY" not in pkg: pkg["NEEDED_BY"] = set()
            pkg["NEEDED_BY"].add(needed_by)
        
        if slot != "": pkg["SLOT"] = slot.replace("\n", " ")
        if inherited != "": pkg["INHERITED"] = inherited.replace("\n", " ")
        if description != "": pkg["DESCRIPTION"] = description.replace("\n", " ")
        if use != "": pkg["USE"] = use.replace("\n", " ")
        if homepage != "": pkg["HOMEPAGE"] = homepage.replace("\n", " ")
        if license != "": pkg["LICENSE"] = license.replace("\n", " ")

        for depend in [rdepend,pdepend]:
            depends = parse_depend(depend)

            # remove specified dependencies
            deps_to_be_removed = set()
            if bestmatch in dep_removals:
                for dep_for_removal in dep_removals[bestmatch]:
                    for depend in depends:
                        if dep_for_removal in vt.dep_match(depend):
                            deps_to_be_removed.add(depend)
            for dep in deps_to_be_removed:
                depends.remove(dep)    

            scan_pkg(depends, dep_removals, pkgs, bestmatch)

    return pkgs

def parse_dep_removals(dep_removals):
    rst = dict()
    if dep_removals is None: return rst
    #else
    for dep in dep_removals:
        pkg, deps = dep.split(":", 1)
        pkg_matches = vt.dep_match(pkg)
        if len(pkg_matches) == 0: raise Exception("no match for '%s'" % pkg)
        elif len(pkg_matches) > 1: raise Exception("multiple matches for '%s'" % pkg)
        #else
        pkg_match = pkg_matches[0]
        if pkg_match not in rst: rst[pkg_match] = set()
        for dep in deps.split(","):
            if dep.strip() == "": continue
            dep_matches = vt.dep_match(dep)
            if len(dep_matches) == 0: raise Exception("no match for '%s'" % dep)
            #else
            for dep_match in dep_matches:
                rst[pkg_match].add(dep_match)
    return rst

def is_path_excluded(path, devel = False):
    exclude_patterns = ["/run/","/var/run/","/var/lock/","/var/cache/"]
    exclude_patterns += ["/usr/src/linux", "/usr/lib/dracut/", "/usr/lib/genpack/"]
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

def resolve_parent(path_str: str) -> Path:
    p = Path(path_str)
    real_parent = p.parent.resolve(strict=False)
    return (real_parent / p.name).as_posix()

def print_all_files_of_all_packages(pkgs, devel):
    logging.debug(f"Printing all files of packages {pkgs}")
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
                    file_to_append = resolve_parent(re.sub(r' [0-9a-f]+ [0-9]+$', "", line[4:]))
                    if not os.path.exists(file_to_append):
                        print(f"# file {file_to_append} does not exist", file=sys.stderr)
                        file_to_append = None
                elif line.startswith("sym "):
                    file_to_append = resolve_parent(re.sub(r' -> .+$', "", line[4:]))
                    if not os.path.islink(file_to_append):
                        print(f"# link {file_to_append} does not exist", file=sys.stderr)
                        file_to_append = None
                if file_to_append is not None and not is_path_excluded(file_to_append, devel):
                    print(file_to_append)

def main(dep_removals={}):
    devel = os.path.isfile("/etc/portage/sets/genpack-devel")
    pkg_sets = ["@genpack-runtime"]
    if devel:
        pkg_sets.append("@genpack-devel")
    pkgs_with_deps = scan_pkg(pkg_sets, dep_removals)

    if os.access("/", os.W_OK):
        os.makedirs("/.genpack", exist_ok=True)
        with open("/.genpack/_pkgs_with_deps.pkl", "wb") as f:
            pickle.dump(pkgs_with_deps, f)
    else:
        with open("pkgs_with_deps.pkl", "wb") as f:
            pickle.dump(pkgs_with_deps, f)

    print_all_files_of_all_packages(pkgs_with_deps, devel)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List files in all runtime packages')
    parser.add_argument("--dep-removal", type=str, action='append', help="Remove dependencies")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    dep_removals = parse_dep_removals(args.dep_removal)

    main(dep_removals)
