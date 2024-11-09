import os,subprocess,logging

MACHINE_ID = "/etc/machine-id"

def configure():
    if os.path.exists(MACHINE_ID): return
    #else
    subprocess.check_call(["systemd-machine-id-setup"])
    logging.info("Machine ID generated.")
