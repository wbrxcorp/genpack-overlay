import os,logging,subprocess

WG_DIR = "/etc/wireguard"
WG_WALBRIX_CONF = os.path.join(WG_DIR, "wg-walbrix.conf")

ETC_WALBRIX_DIR = "/etc/walbrix"
PRIVKEY_FILE = os.path.join(ETC_WALBRIX_DIR, "privkey")

def configure(ini):
    privkey = ini.get("wg-walbrix", "privkey", fallback=None)
    if privkey is None: return
    #else
    privkey_exists = False
    if os.path.isfile(PRIVKEY_FILE):
        existing_privkey = open(PRIVKEY_FILE).read().strip()
        if existing_privkey == privkey:
            privkey_exists = True
        else:
            logging.info("Overwriting existing private key(/etc/walbrix/privkey).")
    if not privkey_exists:
        os.makedirs(ETC_WALBRIX_DIR, exist_ok=True)
        with open(PRIVKEY_FILE, "w") as f:
            f.write(privkey)

    address = ini.get("wg-walbrix", "address", fallback=None)
    if address is None: 
        logging.error("address= not set in [wg-walbrix] section.")
        return
    #else
    pubkey = ini.get("wg-walbrix", "pubkey", fallback="3Wlzo15FB1UjE6yUMMLJWvrtrQHPnbBkzgB8rR4q8VA=")
    endpoint = ini.get("wg-walbrix", "endpoint", fallback="hub.walbrix.net:51821")
    allowed_ips = ini.get("wg-walbrix", "allowed_ips", fallback="fddd:6973:a35e:4507:5523:13ac:9430:c2c9/128")

    os.makedirs(WG_DIR, exist_ok=True)
    with open(WG_WALBRIX_CONF, "w") as f:
        f.write("""[Interface]
PrivateKey=%s
Address=%s
[Peer]
PublicKey=%s
endpoint=%s
AllowedIPs=%s
PersistentKeepalive=25""" % (privkey, address, pubkey, endpoint, allowed_ips))
    os.chmod(WG_WALBRIX_CONF, 0o600)
    subprocess.check_call(["systemctl", "enable", "wg-quick@wg-walbrix"])
    logging.info("WireGuard configuration written to %s" % WG_WALBRIX_CONF)
