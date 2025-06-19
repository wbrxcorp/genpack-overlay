import os,logging

def configure(ini=None):
    timezone_firmware_path = '/sys/firmware/qemu_fw_cfg/by_name/opt/timezone/raw'   
    if not os.path.isfile(timezone_firmware_path): return
    #else
    # read the timezone from the firmware file
    with open(timezone_firmware_path, 'r') as f:
        timezone = f.read().strip()
    if timezone == "": return
    # set the timezone
    if os.path.exists("/etc/localtime"):
        logging.info("Removing existing /etc/localtime")
        os.remove("/etc/localtime")
    # create a symlink to the timezone file
    timezone_path = f"/usr/share/zoneinfo/{timezone}"
    if not os.path.exists(timezone_path):
        logging.error("Timezone file %s does not exist", timezone_path)
        return
    os.symlink(timezone_path, "/etc/localtime")
    logging.info("Timezone set to %s", timezone)