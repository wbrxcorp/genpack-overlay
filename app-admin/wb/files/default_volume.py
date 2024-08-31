import os,subprocess,logging

def configure(ini):
    subvol = "/run/initramfs/rw/vm"
    if not os.path.exists(subvol):
        if subprocess.call(["/sbin/btrfs","subvolume","create",subvol]) != 0:
            logging.warning("Failed to create vm data subvolume under data partition.")

    if os.path.isdir(subvol):
        var_vm_default = "/var/vm/@default"
        os.makedirs(var_vm_default, exist_ok=True)
        if subprocess.call(["mount", "--bind", subvol, var_vm_default]) == 0:
            logging.info("Default VM subvolume mounted.")
            return
    #else
    logging.warning("Default VM subvolume not mounted.")
