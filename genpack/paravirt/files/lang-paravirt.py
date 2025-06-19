import os,logging,re

def configure(ini=None):
    lang_firmware_path = '/sys/firmware/qemu_fw_cfg/by_name/opt/lang/raw'   
    if not os.path.isfile(lang_firmware_path): return
    #else
    # read the LANG from the firmware file
    with open(lang_firmware_path, 'r') as f:
        lang = f.read().strip()
    if lang == "": return

    if os.path.isfile("/etc/profile.env"):
        profile_env = open("/etc/profile.env", 'r').read()
        profile_env = re.sub(r'^export LANG=.*\n', f"export LANG='{lang}'\n", profile_env, flags=re.MULTILINE)
        with open("/etc/profile.env", 'w') as f:
            f.write(profile_env)
        logging.info("LANG set to %s(profile.env)", lang)
        return
    #else
    with open("/etc/locale.conf", 'w') as f:
        f.write(f"LANG=\"{lang}\"\n")
    logging.info("LANG set to %s(locale.conf)", lang)
