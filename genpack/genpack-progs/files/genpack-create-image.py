#!/usr/bin/python3
import sys, os, subprocess, argparse, glob

def main():
    parser = argparse.ArgumentParser(description="Create SquashFS image from upper directory")
    parser.add_argument("upper", help="Path to upper directory")
    parser.add_argument("imageprefix", help="Output image prefix (path without .squashfs extension)")
    parser.add_argument("--compression", default="gzip", choices=["gzip", "xz", "lzo", "none"],
                        help="Compression type (default: gzip)")
    args = parser.parse_args()

    imageprefix = args.imageprefix.removesuffix(".squashfs")
    squashfs_path = f"{imageprefix}.squashfs"

    compression_opts = {
        "gzip": ["-Xcompression-level", "1"],
        "xz":   ["-comp", "xz", "-b", "1M"],
        "lzo":  ["-comp", "lzo"],
        "none": ["-no-compression"],
    }[args.compression]

    print(f"Creating SquashFS image: {squashfs_path} ({args.compression})")
    subprocess.run(
        ["mksquashfs", args.upper, squashfs_path, "-wildcards", "-noappend", "-no-exports"]
        + compression_opts
        + ["-e", "build", "build.d", "build.d/*", "var/log/*.log", "var/tmp/*"],
        check=True
    )

    efi_files = sorted(glob.glob("/usr/lib/genpack-install/*.efi"))
    if not efi_files:
        return

    filesize = os.path.getsize(squashfs_path)
    if filesize >= 4 * 1024 * 1024 * 1024:
        print(f"Warning: {os.path.basename(squashfs_path)} is >= 4GiB, skipping superfloppy image.")
        return

    superfloppy_path = f"{imageprefix}.img"
    superfloppy_tmp = superfloppy_path + ".tmp"
    total_size = ((filesize + 104857600 + 1048575) // 1048576) * 1048576

    print(f"Creating EFI superfloppy image: {superfloppy_path}")
    subprocess.run(["truncate", "-s", str(total_size), superfloppy_tmp], check=True)
    subprocess.run(["mformat", "-i", superfloppy_tmp, "-F", "-h", "255", "-t", "4096", "-n", "32", "::"], check=True)
    subprocess.run(["mmd", "-i", superfloppy_tmp, "::/EFI"], check=True)
    subprocess.run(["mmd", "-i", superfloppy_tmp, "::/EFI/BOOT"], check=True)
    for efi in efi_files:
        subprocess.run(["mcopy", "-i", superfloppy_tmp, efi, f"::/EFI/BOOT/{os.path.basename(efi)}"], check=True)
    subprocess.run(["mcopy", "-i", superfloppy_tmp, squashfs_path, "::/system.img"], check=True)
    os.rename(superfloppy_tmp, superfloppy_path)
    print(f"EFI superfloppy image created: {os.path.basename(superfloppy_path)}")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
