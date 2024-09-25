import os,subprocess,logging

def configure():
    mysql_orig = "/var/lib/mysql"
    if not os.path.isdir(mysql_orig):
        logging.warning("No MySQL data directory")
        return
    #else
    mysql_work = "/run/initramfs/rw/mysql"
    if not os.path.exists(mysql_work):
        if subprocess.call(["/bin/cp", "-a", mysql_orig, mysql_work]) == 0: # somehow shutil.copytree doesn't preserve file owner
            logging.info("MySQL data directory copied.")
        else:
            logging.error("Copying MySQL data directory failed.")

    if os.path.exists(mysql_work) and not os.path.ismount(mysql_orig):
        if subprocess.call(["mount", "--bind", mysql_work, mysql_orig]) == 0:
            logging.info("MySQL data directory bind-mounted.")
        else:
            logging.error("Bind-mounting MySQL Data directory failed.")
