#!/usr/bin/python3
import sys,logging,re,argparse,subprocess
import portage
from portage.dbapi import vartree

vt = vartree.vartree()
api = vartree.vardbapi()

def detect_unwanted_pythons(pkgdb_dir="/var/db/pkg"):
    python_single_target = portage.settings.get("PYTHON_SINGLE_TARGET")
    match = re.match(r'python(.+)', python_single_target)
    if not match:
        raise Exception("Invalid PYTHON_SINGLE_TARGET: %s" % python_single_target)
    #else
    wanted_python_slot = match.group(1).replace("_", ".")
    logging.debug("Wanted Python slot: %s" % wanted_python_slot)

    # find all dev-lang/python-[0-9]* in pkgdb_dir
    python_packages = vt.dep_match("dev-lang/python")
    if len(python_packages) == 1:
        return []
    #else
    if len(python_packages) == 0:
        raise Exception("No Python interpreters installed(WTF?)")

    unwanted_pythons = []
    for p in python_packages:
        slot = api.aux_get(p, ["SLOT"])[0]
        if slot != wanted_python_slot:
            unwanted_pythons.append(p)
    return unwanted_pythons

def unmerge_packages(packages):
    cmdline = ["emerge", "--unmerge"]
    for package in packages:
        cmdline.append('=' + package)
    subprocess.check_call(cmdline)

if __name__ == "__main__":
    progname = sys.argv[0]
    argparser = argparse.ArgumentParser(description="Detect unwanted Python versions")
    argparser.add_argument("--debug", action="store_true", help="Enable debug logging")
    argparser.add_argument("--unmerge", action="store_true", help="Unmerge unwanted Python versions")
    args = argparser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    try:
        unwanted_pythons = detect_unwanted_pythons()
        if len(unwanted_pythons) > 0:
            if args.unmerge:
                logging.info("Unmerging unwanted Python versions: %s" % ",".join(unwanted_pythons))
                unmerge_packages(unwanted_pythons)
            else:
                raise Exception("Unwanted Python versions found: %s. Edit package.mask and run `%s --unmerge` to eliminate them." % (",".join(unwanted_pythons), progname))
        else:
            logging.info("No unwanted Python versions found")
    except Exception as e:
        logging.error(e)
        exit(1)
