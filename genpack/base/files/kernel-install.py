#!/usr/bin/python
import os,glob,subprocess,re

def detect_kernel_and_initramfs():
    kernel = None
    initramfs = None
    latest = 0
    for candidate in ["kernel-*", "vmlinuz-*"]:
        for e in glob.glob(candidate, root_dir="/boot"):
            if e.endswith(".old"): continue
            mtime = os.path.getmtime(os.path.join("/boot", e))
            if mtime < latest: continue
            kernel = e
            latest = mtime
    if kernel is not None:
        for candidate in ["initramfs-", "initrd-"]:
            initramfs = candidate + kernel.split('-', 1)[1] + ".img"
            if os.path.isfile(os.path.join("/boot", initramfs)): break
            #else
            initramfs = None
    return kernel, initramfs

def determine_kernel_package():
    for e in glob.glob("*/*/INHERITED", root_dir="/var/db/pkg"):
        with open(os.path.join("/var/db/pkg", e)) as f:
            if re.search(rf"(?<!\w)kernel-install(?!\w)", f.read()):
                return e.rsplit("/", 1)[0]
    return None

def main():
    kernel_package = determine_kernel_package()
    if kernel_package is None:
        raise Exception("Kernel package not found.")
    #else
    subprocess.check_call(["emerge", "--config", "=" + kernel_package])

    kernel, initramfs = detect_kernel_and_initramfs()
    if not os.path.exists("/boot/kernel") and kernel is not None:
        os.symlink(kernel, "/boot/kernel")
    if not os.path.exists("/boot/initramfs") and initramfs is not None:
        os.symlink(initramfs, "/boot/initramfs")

    os.path.exists("/boot/kernel") and subprocess.check_call(["recursive-touch", "/boot/kernel"])
    os.path.exists("/boot/initramfs") and subprocess.check_call(["recursive-touch", "/boot/initramfs"])

def test():
    kernel, initramfs = detect_kernel_and_initramfs()
    print(kernel, initramfs)
    pkg = determine_kernel_package()
    print(pkg)

if __name__ == "__main__":
    main()
