#!/usr/bin/env python3
import os
import sys
import logging
import pwd

# Initialize basic logging to stderr for manual running
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def truncate_after_second_space(s):
    splitted = s.split(maxsplit=2)
    if len(splitted) < 2: return s
    #else
    return splitted[0] + ' ' + splitted[1]

def main():
    # 1. Fetch raw key string from QEMU fw_cfg
    try:
        from genpack_init import read_qemu_firmware_config
        raw_ssh_pubkeys = read_qemu_firmware_config("opt/ssh-public-key")
    except ImportError:
        # Fallback to direct sysfs reading in case genpack_init is not fully bound
        path = "/sys/firmware/qemu_fw_cfg/by_name/opt/ssh-public-key/raw"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    raw_ssh_pubkeys = f.read()
            except Exception:
                raw_ssh_pubkeys = None
        else:
            raw_ssh_pubkeys = None

    if raw_ssh_pubkeys is None:
        logging.error("No SSH public key found in QEMU fw_cfg (opt/ssh-public-key).")
        sys.exit(1)

    # 2. Parse and normalize keys line by line
    pubkeys = []
    for line in raw_ssh_pubkeys.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pubkeys.append(line)

    if not pubkeys:
        logging.error("No valid SSH public keys found in provided fw_cfg.")
        sys.exit(1)

    # 3. Determine target users based on who runs this command
    uid = os.getuid()
    targets = [] # list of (username, home_dir, uid, gid)

    if uid == 0:
        # If run as root, target root AND all login-enabled interactive standard users
        targets.append(("root", "/root", 0, 0))
        try:
            for entry in pwd.getpwall():
                if 1000 <= entry.pw_uid < 65000:
                    if entry.pw_shell not in ('/bin/false', '/sbin/nologin', '/usr/bin/nologin'):
                        targets.append((entry.pw_name, entry.pw_dir, entry.pw_uid, entry.pw_gid))
        except Exception as e:
            logging.warning(f"Failed to query passwd database: {e}")
    else:
        # If run as a standard user, target ONLY themselves
        try:
            entry = pwd.getpwuid(uid)
            targets.append((entry.pw_name, entry.pw_dir, entry.pw_uid, entry.pw_gid))
        except Exception as e:
            logging.error(f"Failed to identify current user (UID {uid}): {e}")
            sys.exit(1)

    # 4. Apply keys target by target, avoiding duplication
    for username, home_dir, target_uid, target_gid in targets:
        if not home_dir or not os.path.isdir(home_dir):
            continue

        ssh_dir = os.path.join(home_dir, ".ssh")
        authorized_keys = os.path.join(ssh_dir, "authorized_keys")

        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, exist_ok=True)
            os.chmod(ssh_dir, 0o700)
            os.chown(ssh_dir, target_uid, target_gid)
            logging.info(f"Created ssh directory for {username}")

        # Read existing keys to build a lookup set
        existing_keys_normalized = set()
        if os.path.isfile(authorized_keys):
            with open(authorized_keys, "r") as f:
                for line in f:
                    line_strip = line.strip()
                    if line_strip and not line_strip.startswith("#"):
                        existing_keys_normalized.add(truncate_after_second_space(line_strip))

        # Append only missing keys
        added_count = 0
        with open(authorized_keys, "a") as f:
            for pubkey in pubkeys:
                normalized_pubkey = truncate_after_second_space(pubkey)
                if normalized_pubkey not in existing_keys_normalized:
                    f.write(pubkey + "\n")
                    existing_keys_normalized.add(normalized_pubkey)
                    added_count += 1

        if added_count > 0:
            os.chmod(authorized_keys, 0o600)
            os.chown(authorized_keys, target_uid, target_gid)
            logging.info(f"Successfully added {added_count} SSH public key(s) for {username}")
        else:
            logging.info(f"SSH authorized_keys already up-to-date for {username}")

if __name__ == "__main__":
    main()
