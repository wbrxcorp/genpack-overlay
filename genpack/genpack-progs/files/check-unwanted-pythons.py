#!/usr/bin/python3
import os,logging,re,argparse
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

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Detect unwanted Python versions")
    argparser.add_argument("--debug", action="store_true", help="Enable debug logging")
    logging.basicConfig(level=logging.DEBUG if argparser.parse_args().debug else logging.INFO)
    try:
        unwanted_pythons = detect_unwanted_pythons()
        if len(unwanted_pythons) > 0:
            raise Exception("Unwanted Python versions found: %s. Edit package.mask and run `emerge --depclean` to eliminate them." % ",".join(unwanted_pythons))
    except Exception as e:
        logging.error(e)
        exit(1)
    logging.info("Good. only one Python version installed")
