import subprocess, logging, os

def configure():
    if not os.path.exists('/usr/bin/mdb_load'):
        return  # postfix not built with lmdb USE flag, nothing to do

    aliases_lmdb = '/etc/mail/aliases.lmdb'
    if os.path.exists(aliases_lmdb):
        return
    # postfix.service uses ProtectSystem=full with ReadWritePaths=-/etc/mail/aliases.lmdb.
    # The '-' prefix silently ignores the exemption when the file does not exist,
    # so ExecStartPre newaliases fails on first boot.
    # newaliases itself cannot be called here because postfix initialization requires
    # at least one active network interface (own_inet_addr.c), which is not yet
    # available at genpack-init time.
    # Instead, create a valid empty lmdb file using mdb_load (from dev-db/lmdb,
    # already a dependency of mail-mta/postfix[lmdb]), so the ReadWritePaths
    # exemption takes effect and newaliases succeeds at service start.
    empty_db = b'VERSION=3\nformat=bytevalue\nHEADER=END\nDATA=END\n'
    result = subprocess.run(['mdb_load', '-n', aliases_lmdb], input=empty_db, capture_output=True)
    if result.returncode == 0:
        logging.info("postfix: created empty aliases.lmdb")
    else:
        logging.warning("postfix: mdb_load failed: " + result.stderr.decode().strip())
