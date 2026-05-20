#!/usr/bin/python3
"""Shared package enumeration utilities for genpack scripts."""
import os, re
from pathlib import Path

import portage
from portage.dbapi import vartree
from portage.dep import dep_getkey
from portage._sets import load_default_config

vt = vartree.vartree()
api = vartree.vardbapi()

def get_package_set(set_name):
    """Read a portage package set.

    @profile is a Portage built-in set backed by portage._sets; it includes
    all profile packages (both *-marked system packages and non-* ones like
    genpack/base).  portage.settings.packages only returns *-prefixed entries
    and would miss non-system profile packages, so the _sets API is used here.
    All other sets are read from /etc/portage/sets/<name>.
    """
    if set_name == "profile":
        setconfig = load_default_config(portage.settings, portage.db[portage.root])
        sets_map = setconfig.getSets()
        if "profile" not in sets_map:
            return []
        the_set = sets_map["profile"]
        atoms = (the_set.getAtoms() if hasattr(the_set, "getAtoms")
                 else getattr(the_set, "atoms", list(the_set)))
        return [dep_getkey(atom.lstrip("!")) for atom in atoms
                if not str(atom).startswith("-")]
    path = f"/etc/portage/sets/{set_name}"
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return [s for line in f if (s := re.sub(r'#.*', "", line).strip())]

def parse_depend(dep_str):
    if not dep_str:
        return []
    reduced = portage.dep.use_reduce(dep_str)
    pkgs = set()
    idx = 0
    while idx < len(reduced):
        item = reduced[idx]
        if item[0] == "!":
            idx += 1
            continue
        if item == "||":
            for candidate in reduced[idx + 1]:
                if vt.dep_bestmatch(candidate) != "":
                    pkgs.add(candidate)
                    break
            idx += 2
            continue
        pkgs.add(item)
        idx += 1
    return list(pkgs)

def scan_pkg(pkgnames, dep_removals, pkgs=None, needed_by=None):
    """Recursively enumerate installed packages reachable from pkgnames via RDEPEND/PDEPEND."""
    if pkgs is None:
        pkgs = {}
    for pkgname in pkgnames:
        if pkgname[0] == "@":
            pkgs.setdefault(pkgname, {})
            if needed_by is not None:
                pkgs[pkgname].setdefault("NEEDED_BY", set()).add(needed_by)
            scan_pkg(get_package_set(pkgname[1:]), dep_removals, pkgs, pkgname)
            continue

        bestmatch = vt.dep_bestmatch(pkgname)
        if bestmatch == "":
            raise Exception(f"no match for package: {pkgname}")
        if bestmatch in pkgs:
            if needed_by is not None:
                pkgs[bestmatch].setdefault("NEEDED_BY", set()).add(needed_by)
            continue

        rdepend, pdepend, slot, inherited, description, use, homepage, license_ = api.aux_get(
            bestmatch, ["RDEPEND", "PDEPEND", "SLOT", "INHERITED", "DESCRIPTION", "USE", "HOMEPAGE", "LICENSE"])

        if re.search(r'(?<!\w)genpack-ignore(?!\w)', inherited):
            continue

        pkg = {}
        pkgs[bestmatch] = pkg
        if needed_by is not None:
            pkg.setdefault("NEEDED_BY", set()).add(needed_by)
        for key, val in [("SLOT", slot), ("INHERITED", inherited), ("DESCRIPTION", description),
                         ("USE", use), ("HOMEPAGE", homepage), ("LICENSE", license_)]:
            if val:
                pkg[key] = val.replace("\n", " ")

        for dep_str in [rdepend, pdepend]:
            depends = parse_depend(dep_str)
            if bestmatch in dep_removals:
                depends = [d for d in depends
                           if not any(r in vt.dep_match(d) for r in dep_removals[bestmatch])]
            scan_pkg(depends, dep_removals, pkgs, bestmatch)

    return pkgs

def is_path_excluded(path, devel=False):
    always_exclude = ["/run/", "/var/run/", "/var/lock/", "/var/cache/",
                      "/usr/src/linux", "/usr/lib/dracut/", "/usr/lib/genpack/"]
    nodevel_exclude = ["/usr/share/man/", "/usr/share/doc/", "/usr/share/gtk-doc/",
                       "/usr/share/info/", "/usr/include/",
                       re.compile(r'^/usr/lib/python[0-9.]+/test/'),
                       re.compile(r'\.a$')]
    for expr in always_exclude + ([] if devel else nodevel_exclude):
        if isinstance(expr, re.Pattern):
            if expr.search(path): return True
        elif path.startswith(expr):
            return True
    return False

def resolve_parent(path_str):
    p = Path(path_str)
    return (p.parent.resolve(strict=False) / p.name).as_posix()

def collect_files(pkgs_with_deps, devel):
    """Return list of absolute paths owned by packages in pkgs_with_deps."""
    files = []
    for pkg in pkgs_with_deps:
        if pkg[0] == "@":
            continue
        contents_file = f"/var/db/pkg/{pkg}/CONTENTS"
        if not os.path.isfile(contents_file):
            continue
        with open(contents_file) as f:
            for line in f:
                line = re.sub(r'#.*$', "", line).strip()
                if not line:
                    continue
                path = None
                if line.startswith("obj "):
                    path = resolve_parent(re.sub(r' [0-9a-f]+ [0-9]+$', "", line[4:]))
                    if not os.path.exists(path):
                        path = None
                elif line.startswith("sym "):
                    path = resolve_parent(re.sub(r' -> .+$', "", line[4:]))
                    if not os.path.islink(path):
                        path = None
                elif line.startswith("dir "):
                    path = resolve_parent(line[4:].strip())
                    if not os.path.isdir(path):
                        path = None
                if path and not is_path_excluded(path, devel):
                    files.append(path)
    return files

def get_runtime_packages(dep_removals=None):
    """Enumerate @profile + @genpack-runtime (and @genpack-devel if applicable).

    Returns (pkgs_with_deps, devel).
    """
    devel = os.path.isfile("/usr/bin/genpack-devel")
    pkg_sets = ["@profile", "@genpack-runtime"]
    if devel:
        pkg_sets.append("@genpack-devel")
    return scan_pkg(pkg_sets, dep_removals or {}), devel
