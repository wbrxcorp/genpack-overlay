#!/usr/bin/python3
# Runs the per-package post-install scripts. These have to run before the
# artifact's own build scripts, which is why the /.genpack metadata is not
# written here: that describes the finished image and belongs at the end of the
# upper phase -- see genpack-generate-metadata.
import os, glob, logging, argparse, subprocess

from genpack_pkg import get_runtime_packages

import portage

def exec_package_scripts(pkgs_with_deps):
    for pkg in pkgs_with_deps:
        if pkg[0] == "@":
            continue
        pkg_name = portage.versions.pkgsplit(pkg)[0]
        for script in sorted(glob.glob(f"/usr/lib/genpack/package-scripts/{pkg_name}/*")):
            if not os.access(script, os.X_OK):
                continue
            logging.info(f"Executing package script: {script}")
            subprocess.run([script], check=True)

def main():
    logging.info("Enumerating runtime packages...")
    pkgs_with_deps, _ = get_runtime_packages()
    runtime_count = sum(1 for k in pkgs_with_deps if k[0] != "@")
    logging.info(f"Found {runtime_count} runtime packages")

    logging.info("Executing package scripts...")
    exec_package_scripts(pkgs_with_deps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute genpack package scripts")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    main()
