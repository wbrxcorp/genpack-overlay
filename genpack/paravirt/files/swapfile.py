#!/usr/bin/python3
import os,stat,logging,subprocess

SWAPFILE="/dev/vdc"

def is_block_device(path):
    if not os.path.exists(path): return False
    st = os.stat(path)
    return stat.S_ISBLK(st.st_mode)

def configure(ini=None):
    if not is_block_device(SWAPFILE): 
        logging.info("Swapfile not found at %s", SWAPFILE)
        return
    # check if swap is mkswap'ed by calling blkid -o value -s TYPE /dev/vdc
    blkid = subprocess.run(["blkid", "-o", "value", "-s", "TYPE", SWAPFILE], check=False, stdout=subprocess.PIPE)
    if blkid.returncode != 0 or blkid.stdout.decode().strip() != "swap":
        logging.warning("Swapfile is not valid")
        return
    #else
    # swapon /dev/vdc
    logging.info("Enabling swapfile %s", SWAPFILE)
    swapon = subprocess.run(["swapon", SWAPFILE], check=False)
    if swapon.returncode != 0:
        logging.error("Failed to enable swapfile")

if __name__ == '__main__':
    configure()
