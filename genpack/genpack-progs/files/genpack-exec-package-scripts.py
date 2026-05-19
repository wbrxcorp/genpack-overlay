#!/usr/bin/python3
import os, glob, logging, argparse, subprocess

from genpack_pkg import get_runtime_packages

import portage

GENPACK_METADATA_DIR = "/.genpack"

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

def generate_metadata(pkgs_with_deps):
    logging.info(f"Generating metadata in {GENPACK_METADATA_DIR}")
    os.makedirs(GENPACK_METADATA_DIR, exist_ok=True)

    def write_meta(name, content):
        with open(os.path.join(GENPACK_METADATA_DIR, name), "w") as f:
            f.write(content)

    write_meta("arch", os.uname().machine)

    for env_key, meta_name in [("PROFILE", "profile"), ("ARTIFACT", "artifact"), ("VARIANT", "variant")]:
        if env_key in os.environ:
            write_meta(meta_name, os.environ[env_key])

    timestamp_commit = "/var/db/repos/gentoo/metadata/timestamp.commit"
    if os.path.isfile(timestamp_commit):
        write_meta("timestamp.commit", open(timestamp_commit).read())
    else:
        logging.warning("timestamp.commit not found, skipping")

    with open(os.path.join(GENPACK_METADATA_DIR, "packages"), "w") as f:
        for pkgname, pkg in pkgs_with_deps.items():
            if pkgname[0] == "@":
                continue
            header = f"{pkgname}[{pkg['SLOT']}]" if "SLOT" in pkg else pkgname
            f.write(header + "\n")
            if "NEEDED_BY" in pkg:
                f.write("# NEEDED_BY: " + " ".join(pkg["NEEDED_BY"]) + "\n")
            for prop in ["DESCRIPTION", "USE", "HOMEPAGE", "LICENSE"]:
                if prop in pkg:
                    f.write(f"# {prop}: {pkg[prop]}\n")
            f.write("\n")

def main():
    logging.info("Enumerating runtime packages...")
    pkgs_with_deps, _ = get_runtime_packages()
    runtime_count = sum(1 for k in pkgs_with_deps if k[0] != "@")
    logging.info(f"Found {runtime_count} runtime packages")

    logging.info("Executing package scripts...")
    exec_package_scripts(pkgs_with_deps)

    logging.info("Generating metadata...")
    generate_metadata(pkgs_with_deps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute genpack package scripts and generate /.genpack/ metadata")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    main()
