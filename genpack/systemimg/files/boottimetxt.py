import os,logging

def shutdown():
    if not os.access("/run/initramfs/boot", os.W_OK):
        logging.debug("No write access to /run/initramfs/boot.")
        return
    if not os.path.isfile("/run/initramfs/boot/boottime.txt"):
        logging.debug("No boottime.txt found.")
        return
    #else
    os.unlink("/run/initramfs/boot/boottime.txt")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    shutdown()
