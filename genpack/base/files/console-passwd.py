#!/usr/bin/python3
"""Set a console login password without writing to /etc/shadow.

The root filesystem of a genpack image is an overlayfs whose lower layer is the
SquashFS image, and overlayfs copies up whole files: running passwd(1) pins
/etc/shadow to the upper layer, after which users added or removed by later
image updates no longer show up there. This command instead stores per-user
password overrides in the gdbm database that pam_userdb consults from
/etc/pam.d/login (see the console-passwd.sh package-script), leaving
/etc/shadow read-only and the image in charge of the account list.

Consequently only passwords are overridden, only for console logins, and only
for users that already exist -- ssh, su, sudo and display managers keep using
/etc/shadow. Do not use passwd(1) on an overridden user: that leaves both
passwords valid and copies /etc/shadow up after all.
"""

import argparse
import ctypes
import dbm.gnu
import getpass
import os
import pwd
import sys

DB_PATH = "/etc/console-passwd.db"
PAM_LOGIN = "/etc/pam.d/login"


def die(message):
    print("console-passwd: " + message, file=sys.stderr)
    sys.exit(1)


def hash_password(password):
    """Hash with libcrypt's current best method (yescrypt), as passwd(1) would.

    Python dropped the crypt module in 3.13, and openssl passwd would only get
    us $6$, which is weaker than the system default -- so call libcrypt through
    ctypes instead. No extra package is needed: libcrypt comes with the libc.
    """
    lib = None
    for name in ("libcrypt.so.2", "libcrypt.so.1", "libcrypt.so"):
        try:
            lib = ctypes.CDLL(name)
            break
        except OSError:
            continue
    if lib is None:
        die("libcrypt not found")

    lib.crypt_gensalt.restype = ctypes.c_char_p
    lib.crypt_gensalt.argtypes = [ctypes.c_char_p, ctypes.c_ulong,
                                  ctypes.c_char_p, ctypes.c_int]
    lib.crypt.restype = ctypes.c_char_p
    lib.crypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

    # A NULL prefix asks libcrypt for its preferred hashing method.
    setting = lib.crypt_gensalt(None, 0, None, 0)
    if not setting:
        die("crypt_gensalt() failed")
    hashed = lib.crypt(password.encode(), setting)
    # crypt() reports failure by returning NULL or a string starting with '*',
    # which must never be stored: pam_userdb would compare against it verbatim.
    if not hashed or hashed.startswith(b"*"):
        die("crypt() failed")
    return hashed


def read_entries(must_exist=True):
    if not os.path.exists(DB_PATH):
        if must_exist:
            die("%s does not exist; this image was built without the "
                "console-passwd USE flag" % DB_PATH)
        return {}
    with dbm.gnu.open(DB_PATH, "r") as db:
        return {key: db[key] for key in db.keys()}


def write_entries(entries):
    """Replace the database atomically.

    pam_userdb treats an unreadable database as a system error and the PAM
    stack turns that into a refused login for every user, so a half-written
    file must never be visible under DB_PATH.
    """
    tmp_path = DB_PATH + ".new"
    try:
        with dbm.gnu.open(tmp_path, "n", 0o600) as db:
            for user, hashed in entries.items():
                db[user] = hashed
        os.chmod(tmp_path, 0o600)
        os.chown(tmp_path, 0, 0)
        os.replace(tmp_path, DB_PATH)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except KeyError:
        return False


def warn_unless_wired_up():
    """Warn if pam_userdb is not actually consulted at console login.

    The database on its own does nothing; without the PAM stack in place a
    password set here would silently fail to take effect.
    """
    try:
        with open(PAM_LOGIN) as f:
            if DB_PATH in f.read():
                return
    except OSError:
        pass
    print("console-passwd: warning: %s does not reference %s, so the override "
          "will not take effect" % (PAM_LOGIN, DB_PATH), file=sys.stderr)


def do_set(user):
    if not user_exists(user):
        die("no such user: %s (accounts come from the image, not from this "
            "database)" % user)
    warn_unless_wired_up()

    password = getpass.getpass("New console password for %s: " % user)
    if password == "":
        die("empty password refused")
    if password != getpass.getpass("Retype console password for %s: " % user):
        die("passwords do not match")

    entries = read_entries(must_exist=False)
    entries[user.encode()] = hash_password(password)
    write_entries(entries)
    print("Console password for %s updated." % user)


def do_reset(user):
    entries = read_entries()
    if entries.pop(user.encode(), None) is None:
        die("%s has no console password override" % user)
    write_entries(entries)
    print("Console password override for %s removed; the password from the "
          "image applies again." % user)


def do_list():
    entries = read_entries()
    if not entries:
        print("No console password overrides.")
        return
    for user in sorted(entries):
        name = user.decode(errors="replace")
        print("%s%s" % (name, "" if user_exists(name) else "\t(no such user)"))


def do_check():
    orphans = [user.decode(errors="replace") for user in read_entries()
               if not user_exists(user.decode(errors="replace"))]
    if not orphans:
        print("No orphan entries.")
        return
    # An image update that drops a user leaves its entry behind. Harmless on
    # its own (pam_userdb never authenticates a user the account phase does not
    # know), but it should not rot there unnoticed.
    for user in sorted(orphans):
        print("orphan entry: %s" % user)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Set a console login password without touching /etc/shadow.")
    parser.add_argument("user", nargs="?", help="user to operate on")
    parser.add_argument("--reset", action="store_true",
                        help="drop the override and fall back to the image's password")
    parser.add_argument("--list", action="store_true",
                        help="list overridden users (never hashes)")
    parser.add_argument("--check", action="store_true",
                        help="report entries whose user no longer exists")
    args = parser.parse_args()

    if sum([args.reset, args.list, args.check]) > 1:
        parser.error("--reset, --list and --check are mutually exclusive")
    if (args.list or args.check) and args.user is not None:
        parser.error("--list and --check take no user")
    if not (args.list or args.check) and args.user is None:
        parser.error("no user given")

    if os.geteuid() != 0:
        die("must be run as root")

    if args.list:
        do_list()
    elif args.check:
        do_check()
    elif args.reset:
        do_reset(args.user)
    else:
        do_set(args.user)


if __name__ == "__main__":
    main()
