#!/usr/bin/python3
import os, time, logging, argparse, subprocess, tempfile

from genpack_pkg import get_runtime_packages, collect_files

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

# Top-level paths that may not be owned by any package (created by stage3 bootstrap)
# but must be present in the runtime image.
_EXTRA_TOPLEVEL = [
    "/bin", "/sbin", "/lib", "/lib64", "/usr/sbin",
    "/run", "/proc", "/sys", "/root", "/home", "/tmp", "/mnt",
]

def _collect_extra_via_raw(raw_root):
    """Collect stage3-bootstrap paths that packages don't own, via bind-mount raw root.

    Returns absolute path strings ready to pass to _do_copyup().
    /dev is excluded here — device nodes cannot be copy-upped inside the nspawn
    user namespace; they are handled by 'genpack-helper copyup-dev' on the host.
    """
    extras = []
    for path in _EXTRA_TOPLEVEL:
        if os.path.lexists(os.path.join(raw_root, path.lstrip("/"))):
            extras.append(path)
    return extras

def copyup_files(files):
    raw_root = tempfile.mkdtemp(prefix="genpack-copyup-")
    try:
        subprocess.run(["mount", "--bind", "/", raw_root], check=True)
        try:
            extra = _collect_extra_via_raw(raw_root)
            seen = set(files)
            merged = list(files)
            for f in extra:
                if f not in seen:
                    merged.append(f)
                    seen.add(f)
            _do_copyup(merged, raw_root)
        finally:
            subprocess.run(["umount", raw_root], check=True)
    finally:
        os.rmdir(raw_root)

def _do_copyup(files, raw_root):
    touched = 0
    errors = 0

    with logging_redirect_tqdm():
        for path in tqdm(files, desc="copy-up", unit="files"):
            raw_path = os.path.join(raw_root, path.lstrip("/"))
            if not os.path.lexists(raw_path):
                logging.debug(f"path gone (removed by script?): {path}")
                continue
            try:
                st = os.lstat(raw_path)
                os.utime(raw_path, (time.time(), st.st_mtime), follow_symlinks=False)
                touched += 1
            except OSError as e:
                tqdm.write(f"WARNING: utime failed: {path}: {e}")
                errors += 1

    logging.info(f"Copy-up triggered: {touched} files, {errors} errors")

def main():
    logging.info("Enumerating runtime packages...")
    pkgs_with_deps, devel = get_runtime_packages()
    runtime_count = sum(1 for k in pkgs_with_deps if k[0] != "@")
    logging.info(f"Found {runtime_count} runtime packages")

    logging.info("Collecting runtime files...")
    files = collect_files(pkgs_with_deps, devel)
    logging.info(f"Found {len(files)} files to copy-up")

    logging.info("Triggering overlayfs copy-up via utime...")
    copyup_files(files)

    logging.info("genpack-copyup complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger overlayfs copy-up for all runtime package files")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    main()
