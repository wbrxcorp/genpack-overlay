#!/usr/bin/python3
import os,sys,subprocess,logging,glob,pickle,argparse

import portage

genpack_metadata_dir = "/.genpack"
dry_run = os.geteuid() != 0

def exec_package_scripts(pkgs_with_deps):
    for pkg in pkgs_with_deps.keys():
        if pkg[0] == '@': continue
        #else
        for f in sorted(glob.glob("/usr/lib/genpack/package-scripts/%s/*" % (portage.versions.pkgsplit(pkg)[0]))):
            if not os.access(f, os.X_OK): continue
            #else
            logging.info(f"Executing package script {f}")
            if dry_run:
                logging.info(f"Dry run: {f}")
            else:
                subprocess.run([f], check=True)

class MetadataFileForWriting:
    def __init__(self, metadata_filename):
        if dry_run:
            self._f = None
            logging.info(f"Dry run: writing metadata to stdout for {metadata_filename}")
        else:
            self._f = open(os.path.join(genpack_metadata_dir, metadata_filename), "w")

    def write(self, data):
        if self._f is None:
            logging.info(data.strip())
            return len(data)
        return self._f.write(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._f is not None:
            self._f.close()    

def generate_metadata(pkgs_with_deps):
    logging.info("Generating metadata under /.genpack")
    os.makedirs(genpack_metadata_dir, exist_ok=True)

    with MetadataFileForWriting("arch") as f:
        f.write(os.uname().machine)
    if "PROFILE" in os.environ:
        with MetadataFileForWriting("profile") as f:
            f.write(os.environ["PROFILE"])
    if "ARTIFACT" in os.environ:
        with MetadataFileForWriting("artifact") as f:
            f.write(os.environ["ARTIFACT"])
    if "VARIANT" in os.environ:
        with MetadataFileForWriting("variant") as f:
            f.write(os.environ["VARIANT"])
    portage_dir = "/var/db/repos/gentoo"
    if os.path.isdir(portage_dir):
        with MetadataFileForWriting("timestamp.commit") as f:
            f.write(open(os.path.join(portage_dir, "metadata/timestamp.commit")).read())
    else:
        logging.warning(f"Portage directory {portage_dir} does not exist, skipping timestamp.commit generation")
    with MetadataFileForWriting("packages") as f:
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

def main():
    if os.path.isfile("pkgs_with_deps.pkl"):
        logging.info("Loading package dependency data from pkgs_with_deps.pkl in the current directory")
        with open("/.genpack/_pkgs_with_deps.pkl", "rb") as f:
            pkgs_with_deps = pickle.load(f)
    else:
        with open("/.genpack/_pkgs_with_deps.pkl", "rb") as f:
            pkgs_with_deps = pickle.load(f)

    exec_package_scripts(pkgs_with_deps)
    generate_metadata(pkgs_with_deps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute package scripts and generate metadata.")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode (do not execute scripts, just log actions)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    if args.dry_run:
        dry_run = True
    
    if dry_run:
        logging.info("Dry run mode enabled")

    main()
