import os,subprocess,logging

def is_btrfs_mounted(mountpoint):
    with open("/proc/mounts") as f:
        for line in f:
            splitted = line.split()
            if line.split()[1] == mountpoint and line.split()[2] == "btrfs":
                return True
    return False

def configure(ini):
    rw_layer = "/run/initramfs/rw"
    subvol = os.path.join(rw_layer, "vm")
    if not os.path.exists(subvol):
        if is_btrfs_mounted(rw_layer):
            if subprocess.call(["/sbin/btrfs","subvolume","create",subvol]) != 0:
                logging.warning("Failed to create vm data subvolume under data partition.")
        else:
            logging.warning("Data partition is not mounted as btrfs. Falling back to regular directory")
            os.makedirs(subvol, exist_ok=True)

    if os.path.isdir(subvol):
        var_vm_default = "/var/vm/@default"
        os.makedirs(var_vm_default, exist_ok=True)
        if subprocess.call(["mount", "--bind", subvol, var_vm_default]) == 0:
            logging.info("Default VM subvolume mounted.")
            return
    #else
    logging.warning("Default VM subvolume not mounted.")

if __file__ == "__main__":
    configure(None)