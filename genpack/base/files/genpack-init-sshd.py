import os,logging

def truncate_after_second_space(s):
    splitted = s.split(maxsplit=2)
    if len(splitted) < 2: return s
    #else
    return splitted[0] + ' ' + splitted[1]

def configure(ini):
    ssh_pubkey = ini.get("_default", "ssh_pubkey", fallback=None)
    if ssh_pubkey is None: return
    #else
    ssh_dir = "/root/.ssh"
    authorized_keys = os.path.join(ssh_dir, "authorized_keys")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, exist_ok=True)
        os.chmod(ssh_dir, 0o700)
        logging.info("root ssh directory created")
    already_set = False
    if os.path.isfile(authorized_keys):
        with open(authorized_keys, "r") as f:
            for line in f:
                if truncate_after_second_space(line) == ssh_pubkey:
                    already_set = True
                    break
    if already_set:
        logging.info("root ssh authorized_keys already set")
        return
    #else
    with open(authorized_keys, "a") as f:
        f.write(ssh_pubkey + "\n")
    logging.info("root ssh authorized_keys set")
