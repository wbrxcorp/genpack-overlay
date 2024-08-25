#!/usr/bin/python
import os,glob

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

def main():
    kernel, initramfs = detect_kernel_and_initramfs()
    if not os.path.exists("/boot/kernel") and kernel is not None:
        os.symlink(kernel, "/boot/kernel")
    if not os.path.exists("/boot/initramfs") and initramfs is not None:
        os.symlink(initramfs, "/boot/initramfs")

if __name__ == "__main__":
    main()
