import os
import logging
import pwd

def truncate_after_second_space(s):
    splitted = s.split(maxsplit=2)
    if len(splitted) < 2: return s
    #else
    return splitted[0] + ' ' + splitted[1]

def configure(ini):
    # 1. Fetch raw key string from system.ini
    raw_ssh_pubkeys = ini.get("_default", "ssh_pubkey", fallback=None)

    if raw_ssh_pubkeys is None:
        logging.info("No SSH public key found in system.ini.")
        return

    # 2. Parse and normalize keys line by line (handles multi-line inputs cleanly)
    pubkeys = []
    for line in raw_ssh_pubkeys.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pubkeys.append(line)

    if not pubkeys:
        logging.info("No valid SSH public keys found in provided config.")
        return

    # 3. Identify all target interactive users for key distribution
    targets = [("root", "/root", 0, 0)]
    try:
        for entry in pwd.getpwall():
            if 1000 <= entry.pw_uid < 65000:
                if entry.pw_shell not in ('/bin/false', '/sbin/nologin', '/usr/bin/nologin'):
                    targets.append((entry.pw_name, entry.pw_dir, entry.pw_uid, entry.pw_gid))
    except Exception as e:
        logging.warning(f"Failed to query passwd database: {e}")

    # 4. Safely apply keys target by target, avoiding duplication at line-level
    for username, home_dir, uid, gid in targets:
        if not home_dir or not os.path.isdir(home_dir):
            continue

        ssh_dir = os.path.join(home_dir, ".ssh")
        authorized_keys = os.path.join(ssh_dir, "authorized_keys")

        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, exist_ok=True)
            os.chmod(ssh_dir, 0o700)
            os.chown(ssh_dir, uid, gid)
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
            os.chown(authorized_keys, uid, gid)
            logging.info(f"Added {added_count} SSH public key(s) for {username}")
        else:
            logging.info(f"SSH authorized_keys already up-to-date for {username}")
