import os,subprocess,logging

def configure():
    if os.path.exists("/etc/walbrix/privkey"): 
        logging.debug("/etc/walbrix/privkey already exists")
        return
    #else
    if subprocess.call(["/usr/bin/wb", "wg", "genkey"]) == 0:
        logging.info("Private key generated.")
    else:
        logging.error("Generating private key failed.")