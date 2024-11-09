import os,subprocess,logging

def configure():
    mysql_orig = "/var/lib/mysql"
    if not os.path.isdir(mysql_orig):
        logging.warning("No MySQL data directory")
        return
    #else

    if not os.path.exists("/run/initramfs/rw"):
        logging.error("No /run/initramfs/rw") # impossible, though
        return

    mysql_work = "/run/initramfs/rw/mysql"
    if not os.path.exists(mysql_work):
        # check if available capacity of /run/initramfs/rw is enough
        statvfs = os.statvfs("/run/initramfs/rw")
        if statvfs.f_bavail * statvfs.f_frsize < 1024 * 1024 * 768: # 768MB
            logging.error("Insufficient space in /run/initramfs/rw (initramfs?)")
            return
        #else

        if subprocess.call(["/bin/cp", "-a", mysql_orig, mysql_work]) == 0: # somehow shutil.copytree doesn't preserve file owner
            logging.info("MySQL data directory copied.")
        else:
            logging.error("Copying MySQL data directory failed.")

    if os.path.exists(mysql_work) and not os.path.ismount(mysql_orig):
        if subprocess.call(["mount", "--bind", mysql_work, mysql_orig]) == 0:
            logging.info("MySQL data directory bind-mounted.")
        else:
            logging.error("Bind-mounting MySQL Data directory failed.")
