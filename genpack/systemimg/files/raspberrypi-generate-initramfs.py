#!/usr/bin/python3
import os,glob,subprocess

modules_dir = "/usr/lib/modules"

def get_kernel_version(pattern):
    latest_kernel_ver = None
    kernel_vers = glob.glob(pattern, root_dir=modules_dir)
    for kernel_ver in kernel_vers:
        kernel_dir = os.path.join(modules_dir, kernel_ver)
        if not os.path.isdir(kernel_dir): continue
        #else
        latest_kernel_dir = os.path.join(modules_dir, latest_kernel_ver) if latest_kernel_ver else None
        if latest_kernel_dir is None or os.stat(kernel_dir).st_mtime > os.stat(latest_kernel_dir).st_mtime:
            latest_kernel_ver = kernel_ver
    return latest_kernel_ver

def generate_initramfs(kver, output):
    subprocess.check_call(["dracut", "--compress", "gzip", "--force", "--kver", kver, output])

def main():
    # glob modules_dir/*-v8+
    armv8_kernel_ver = get_kernel_version("*-v8+")
    if armv8_kernel_ver is not None:
        print("Generating initramfs image for armv8 kernel version: %s" % armv8_kernel_ver)
        generate_initramfs(armv8_kernel_ver, "/boot/initramfs8")
    armv8_16k_kernel_ver = get_kernel_version("*-v8-16k+")
    if armv8_16k_kernel_ver is not None:
        print("Generating initramfs image for armv8-16k kernel version: %s" % armv8_16k_kernel_ver)
        generate_initramfs(armv8_16k_kernel_ver, "/boot/initramfs_2712")

    # append 'auto_initramfs=1' line to /boot/config.txt if not exists
    with open("/boot/config.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() == "auto_initramfs=1":
                return

    with open("/boot/config.txt", "a") as f:
        f.write("\nauto_initramfs=1\n")

if __name__ == "__main__":
    main()