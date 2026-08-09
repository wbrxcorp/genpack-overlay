import logging

from genpack_init_helper import merge_env_file

def configure(ini):
    locale = ini.get("_default", "locale", fallback=None)
    if locale is None: return
    #else

    # locale.conf covers system services, environment covers console and ssh
    # logins plus systemd user instances.  Neither one reaches all three.
    merge_env_file("/etc/locale.conf", "LANG", locale)
    merge_env_file("/etc/environment", "LANG", locale)

    logging.info("Locale set to {}".format(locale))
