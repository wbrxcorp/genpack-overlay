import logging

def configure(ini):
    locale = ini.get("_default", "locale", fallback=None)
    if locale is None: return
    #else

    with open("/etc/locale.conf", "w") as f:
        f.write("LANG={}\n".format(locale))

    logging.info("Locale set to {}".format(locale))