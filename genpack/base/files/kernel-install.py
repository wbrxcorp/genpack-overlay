#!/usr/bin/python
import os,glob,subprocess,re

def decompress_kernel_if_necessary(kernel):
    # decompress kernel if compressed by CONFIG_EFI_ZBOOT
    kernel_bin = None
    with open(kernel, "rb") as f:
        kernel_bin = f.read()
        if len(kernel_bin) < 32 or kernel_bin[0:8] != b"MZ\x00\x00zimg" or kernel_bin[24:28] != b"gzip": return False
    #else
    gzip_offset = kernel_bin.find(b"\x1f\x8b\x08\x00\x00\x00\x00\x00")
    if gzip_offset < 0:
        print("Kernel compressed but gzip header not found: %s" % kernel)
        return False
    #else
    print("Decompressing compressed kernel %s..." % kernel)
    decompressed_kernel = kernel + ".decompressed"
    with open(decompressed_kernel, "wb") as f:
        subprocess.Popen(["gunzip", "-c"], stdin=subprocess.PIPE, stdout=f).communicate(input=kernel_bin[gzip_offset:])
    os.rename(decompressed_kernel, kernel)

    return True

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
    if kernel is not None:
        decompress_kernel_if_necessary(os.path.join("/boot", kernel))
        if not os.path.exists("/boot/kernel"):
            os.symlink(kernel, "/boot/kernel")
    if not os.path.exists("/boot/initramfs") and initramfs is not None:
        os.symlink(initramfs, "/boot/initramfs")

def test():
    kernel, initramfs = detect_kernel_and_initramfs()
    print(kernel, initramfs)
    pkg = determine_kernel_package()
    print(pkg)

if __name__ == "__main__":
    main()
