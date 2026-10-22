#!/usr/bin/python3
# Writes the /.genpack metadata that describes the image.
#
# It runs after the artifact's files/ merge and build scripts, because what it
# writes describes the finished image. Metadata an artifact brings in by accident
# -- files/ assembled from another image's root carries that image's /.genpack
# along -- therefore does not end up describing this one, and the package list
# reflects the runtime set as the upper phase left it.
#
# That list starts from @profile and @genpack-runtime, not from @world or the
# vdb, so a package a build script merges without touching the sets is missing
# from it however late this runs -- and then goes unchecked by glsa-check in the
# running image. Fixing that means changing how the list is derived, not when.
#
# The metadata mostly comes from environment variables genpack passes in. The
# names genpack owns are the ENV_METADATA below, plus genpack.md (re-placed by
# this script from genpack/base's copy, see PRIMER_SOURCE). banner (written by
# the genpack/base[banner] package script, and meant to stay overridable) and
# whatever the artifact keeps here itself are left alone. A name genpack has no
# value for is unlinked rather than left as found, so a file carried in from
# elsewhere cannot pass for generated metadata.
#
# None of this makes the metadata proof against an artifact that sets out to
# forge it -- build scripts run as root and can replace the very commands genpack
# invokes here. Recording provenance assumes the artifact definition is trusted.
import os, shutil, logging, argparse

from genpack_pkg import get_runtime_packages

GENPACK_METADATA_DIR = "/.genpack"

# Environment variable -> metadata file name. COMMIT_ID is the artifact
# definition's git revision, determined on the host by genpack. Not to be
# confused with timestamp.commit, which is the Portage tree's.
ENV_METADATA = [
    ("PROFILE", "profile"),
    ("ARTIFACT", "artifact"),
    ("VARIANT", "variant"),
    ("COMMIT_ID", "commit-id"),
]

# The primer genpack/base stages for agents that log into a built artifact. It
# lives in the staging directory /usr/lib/genpack/, which genpack-copyup excludes
# from every image, so the primer only reaches a runtime image through this copy:
# /.genpack/ is genpack's own namespace and is never trimmed. Copying from the
# staged package file instead of trusting what is already in the upper layer keeps
# the copy aligned with the genpack/base version actually in the image, and
# overwrites one carried in by files/.
PRIMER_SOURCE = "/usr/lib/genpack/genpack.md"
PRIMER_NAME = "genpack.md"

def clear(path):
    """Remove path if it exists, symlinks and directories included.

    Everything genpack owns goes through here first. files/ is merged with cp -rd,
    which preserves symlinks, and open(..., "w") on a symlink writes through to
    wherever it points, so clearing the path first keeps metadata generation from
    writing outside its own directory whatever it finds there.
    """
    if not os.path.lexists(path):
        return False
    #else
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
    return True

def generate_metadata(pkgs_with_deps):
    logging.info(f"Generating metadata in {GENPACK_METADATA_DIR}")
    if not os.path.isdir(GENPACK_METADATA_DIR) or os.path.islink(GENPACK_METADATA_DIR):
        if clear(GENPACK_METADATA_DIR):
            logging.warning(f"{GENPACK_METADATA_DIR} was not a directory, replaced it")
    os.makedirs(GENPACK_METADATA_DIR, exist_ok=True)

    def write_meta(name, content):
        path = os.path.join(GENPACK_METADATA_DIR, name)
        clear(path)
        with open(path, "w") as f:
            f.write(content)

    def remove_meta(name):
        # "not generated" has to mean "not present", or a file that arrived with
        # files/ would read as metadata genpack wrote
        if clear(os.path.join(GENPACK_METADATA_DIR, name)):
            logging.warning(f"Removed {name}, which genpack has no value for")

    write_meta("arch", os.uname().machine)

    for env_key, meta_name in ENV_METADATA:
        if env_key in os.environ:
            write_meta(meta_name, os.environ[env_key])
        else:
            remove_meta(meta_name)

    timestamp_commit = "/var/db/repos/gentoo/metadata/timestamp.commit"
    if os.path.isfile(timestamp_commit):
        write_meta("timestamp.commit", open(timestamp_commit).read())
    else:
        logging.warning("timestamp.commit not found, skipping")
        remove_meta("timestamp.commit")

    clear(os.path.join(GENPACK_METADATA_DIR, "packages"))
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

    primer = os.path.join(GENPACK_METADATA_DIR, PRIMER_NAME)
    if os.path.isfile(PRIMER_SOURCE):
        clear(primer)
        shutil.copyfile(PRIMER_SOURCE, primer)
        logging.info(f"Placed {PRIMER_SOURCE} as {primer}")
    else:
        if clear(primer):
            logging.warning(f"{PRIMER_SOURCE} not found (genpack/base too old), removed {primer}")
        else:
            logging.warning(f"{PRIMER_SOURCE} not found (genpack/base too old), skipping {PRIMER_NAME}")

def main():
    logging.info("Enumerating runtime packages...")
    pkgs_with_deps, _ = get_runtime_packages()
    runtime_count = sum(1 for k in pkgs_with_deps if k[0] != "@")
    logging.info(f"Found {runtime_count} runtime packages")

    generate_metadata(pkgs_with_deps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate /.genpack/ metadata describing the image")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    main()
