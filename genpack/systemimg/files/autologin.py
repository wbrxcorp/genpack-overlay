import os,logging,subprocess

def configure(root, ini):
    autologin = ini.getboolean("_default", "autologin", fallback=None)
    if autologin is None: 
        logging.debug("leaving autologin configuration.")
        return
    #else
    service_dir = os.path.join(root, "etc/systemd/system/getty@tty1.service.d")
    conf_file = os.path.join(service_dir, "autologin-configured-by-overlay-init.conf")
    if autologin:
        os.makedirs(service_dir, exist_ok=True)
        with open(conf_file, "w") as f:
            f.write("[Service]\n")
            f.write("ExecStart=\n")
            f.write("ExecStart=-/sbin/agetty --autologin root --noclear %I 38400 linux\n")
        logging.info("Autologin enabled.")
    else:
        if os.path.isfile(conf_file): os.unlink(conf_file)
        logging.info("Autologin disabled.")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "restart", "getty@tty1"], check=True)
