import os
import logging
import subprocess
from genpack_init import get_mount_info, rw_path, read_qemu_firmware_config

def configure():
    # Attempt to read fw_cfg opt/ssh-public-key
    raw_pubkey = read_qemu_firmware_config("opt/ssh-public-key")
    if not raw_pubkey:
        logging.info("No SSH public key found in QEMU fw_cfg.")
        return

    # Check if transient mode (upper fs /run/initramfs/rw is tmpfs) using our new native get_mount_info
    try:
        info = get_mount_info(rw_path())
        is_transient = (info.get("fstype") == "tmpfs")
    except Exception as e:
        logging.warning(f"Failed to check mount filesystem info: {e}")
        is_transient = False

    if is_transient:
        logging.info("Transient (tmpfs) mode detected. Automatically executing import-fw-ssh-key...")
        try:
            # Execute our helper tool to deploy to root and all standard interactive users
            if os.path.exists("/usr/bin/import-fw-ssh-key"):
                subprocess.run(["/usr/bin/import-fw-ssh-key"], check=True)
            else:
                logging.warning("/usr/bin/import-fw-ssh-key not found. Skipping auto-deploy.")
        except Exception as e:
            logging.error(f"Failed to automatically import SSH keys: {e}")
    else:
        logging.info("SSH public keys were detected in fw_cfg but not automatically deployed (not in transient/tmpfs mode). "
                     "You can manually import them by running: import-fw-ssh-key")
