import os,shutil,logging

def configure(ini):
    efi_path = "/run/initramfs/boot/efi/boot/memtest86.efi"
    if os.path.exists(efi_path): 
        logging.debug("memtest86 EFI binary already installed")
        return
    boot_path = "/boot/memtest86-bin.efi"
    if not os.path.isfile(boot_path): return
    os.makedirs(os.path.dirname(efi_path), exist_ok=True)
    shutil.copyfile(boot_path, efi_path)
    logging.info("memtest86 EFI application copied to /efi/boot.")
