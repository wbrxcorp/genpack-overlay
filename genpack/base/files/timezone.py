import os,logging

def configure(ini):
    timezone = ini.get("_default", "timezone", fallback=None)
    if timezone is None: return
    #else

    # do ln -sf /usr/share/zoneinfo/{timezone} /etc/localtime
    try:
        os.symlink("/usr/share/zoneinfo/{}".format(timezone), "/etc/localtime")
    except FileExistsError:
        os.remove("/etc/localtime")
        os.symlink("/usr/share/zoneinfo/{}".format(timezone), "/etc/localtime")
    logging.info("Timezone set to {}".format(timezone))
