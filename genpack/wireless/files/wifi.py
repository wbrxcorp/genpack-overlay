import os,subprocess,glob,logging,time

def get_wireless_interface_name(wait):
    for i in range(0, wait):
        for interface in glob.glob("/sys/class/net/wl*"):
            if os.path.isdir(os.path.join(interface, "wireless")):
                return os.path.basename(interface)
        logging.debug("Waiting for WiFi interface to be activated...")
        time.sleep(1)
    return None

def configure(ini):
    wifi_ssid = ini.get("_default", "wifi_ssid", fallback=None)
    if wifi_ssid is None:
        logging.debug("Leaving WiFi configuration.")
        return
    #else
    for conf in glob.glob("/etc/wpa_supplicant/wpa_supplicant-*.conf"):
        os.unlink(conf)
        logging.debug("%s removed" % conf)
    for link in glob.glob("/etc/systemd/system/multi-user.target.wants/wpa_supplicant@*.service"):
        os.unlink(link)
        logging.debug("%s removed" % link)

    interface = ini.get("_default", "wifi_interface", fallback=None)    
    if interface is None: interface = get_wireless_interface_name(ini.getint("_default", "wifi_wait", fallback=3))

    if interface is None:
        logging.warning("Wireless interface not found.")
        return

    #else
    logging.info("Using wireless interface %s." % interface)

    conf = "/etc/wpa_supplicant/wpa_supplicant-%s.conf" % interface
    with open(conf, "w") as f:
        f.write('network={\n\tssid="%s"\n' % wifi_ssid)
        wifi_key = ini.get("_default", "wifi_key", fallback=None)
        if wifi_key is not None:
            f.write('\tpsk="%s"\n' % wifi_key)
        f.write('}')
        logging.debug("%s created" % conf)

    subprocess.run(["systemctl", "enable", "wpa_supplicant@%s" % interface], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    logging.info("Service wpa_supplicant@%s enabled." % interface)

if __name__ == "__main__":
    pass
