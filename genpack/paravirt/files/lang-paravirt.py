import os,logging

from genpack_init_helper import merge_env_file

def configure(ini=None):
    lang_firmware_path = '/sys/firmware/qemu_fw_cfg/by_name/opt/lang/raw'
    if not os.path.isfile(lang_firmware_path): return
    #else
    # read the LANG from the firmware file
    with open(lang_firmware_path, 'r') as f:
        lang = f.read().strip()
    if lang == "": return

    # /etc/profile.env used to be written here instead, which left system
    # services on a different locale and pinned that file into the overlayfs
    # upper layer on the first boot, so later image updates to it never applied.
    merge_env_file("/etc/locale.conf", "LANG", lang)
    merge_env_file("/etc/environment", "LANG", lang)
    logging.info("LANG set to %s", lang)
