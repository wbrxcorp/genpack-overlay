import os,logging

def configure(root, ini):
    hostname = ini.get("_default", "hostname", fallback=None)
    if hostname is None: 
        logging.debug("Hostname not set")
        return
    #else
    with open(os.path.join(root, "etc/hostname"), "w") as f:
        f.write(hostname)
    logging.info("Hostname: %s" % hostname)
