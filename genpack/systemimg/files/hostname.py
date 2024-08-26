import logging

def configure(ini):
    hostname = ini.get("_default", "hostname", fallback=None)
    if hostname is None: 
        logging.debug("Hostname not set")
        return
    #else
    with open("/etc/hostname", "w") as f:
        f.write(hostname)
    logging.info("Hostname: %s" % hostname)
