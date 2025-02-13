import logging,time

from genpack_init import root_path,coldplug,enable_systemd_service

def get_wireless_interface_name(wait):
    for i in range(0, wait):
        for interface in root_path("/sys/class/net").glob("wl*"):
            logging.debug("Looking for directory wireless in %s" % interface)
            if interface.joinpath("wireless").is_dir():
                return interface.name
        logging.debug("Waiting for WiFi interface to be activated...")
        time.sleep(1)
    return None

def configure(ini):
    wifi_ssid = ini.get("_default", "wifi_ssid", fallback=None)
    if wifi_ssid is None:
        logging.debug("Leaving WiFi configuration.")
        return
    #else
    logging.debug("WiFi SSID: %s" % wifi_ssid)
    wpa_supplicant_dir = root_path("/etc/wpa_supplicant")
    wpa_supplicant_dir.mkdir(parents=True,exist_ok=True)
    for conf in wpa_supplicant_dir.glob("wpa_supplicant-*.conf"):
        conf.unlink()
        logging.debug("%s removed" % conf)
    for link in root_path("/etc/systemd/system/multi-user.target.wants").glob("wpa_supplicant@*.service"):
        link.unlink()
        logging.debug("%s removed" % link)

    coldplug()

    interface = ini.get("_default", "wifi_interface", fallback=None)    
    if interface is None: interface = get_wireless_interface_name(ini.getint("_default", "wifi_wait", fallback=3))

    if interface is None:
        logging.warning("Wireless interface not found.")
        return

    #else
    logging.info("Using wireless interface %s." % interface)

    wpa3 = ini.getboolean("_default", "wifi_wpa3", fallback=False)
    sae_pwe = ini.getint("_default", "wifi_sae_pwe", fallback=2 if wpa3 else None)

    conf = wpa_supplicant_dir.joinpath("wpa_supplicant-%s.conf" % interface)
    with open(conf, "w") as f:
        if sae_pwe is not None:
            f.write("sae_pwe=%d\n" % sae_pwe)
        f.write('network={\n\tssid="%s"\n' % wifi_ssid)
        wifi_key = ini.get("_default", "wifi_key", fallback=None)
        if wifi_key is not None:
            if wpa3:
                f.write('\tkey_mgmt=SAE\n')
                f.write('\tsae_password="%s"\n' % wifi_key)
                f.write('\tieee80211w=2\n')
            else:
                f.write('\tpsk="%s"\n' % wifi_key)
        else:
            f.write('\tkey_mgmt=NONE\n')
            logging.warning("WiFi key not set.  Using key_mgmt=NONE.")
        f.write('}\n')
        logging.debug("%s created" % conf)

    enable_systemd_service("wpa_supplicant@%s" % interface)

# mkdir sys/class/net/wlan0/wireless
# PYTHONPATH=/path/to/mock python3 wifi.py
if __name__ == "__main__":
    import argparse,configparser
    logging.basicConfig(level=logging.DEBUG)

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wpa3", default=False, action="store_true")
    argparser.add_argument("--public-wifi", default=False, action="store_true")
    args = argparser.parse_args()

    ini = configparser.ConfigParser()
    ini.add_section("_default")
    ini.set("_default", "wifi_ssid", "my_wifi")
    if not args.public_wifi:
        ini.set("_default", "wifi_key", "my_password")
    if args.wpa3:
        ini.set("_default", "wifi_wpa3", "yes")
    configure(ini)
