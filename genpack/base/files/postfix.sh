#!/bin/sh
# postfix.service uses ProtectSystem=full, making /etc read-only.
# ReadWritePaths exempts aliases.lmdb, but the leading '-' means the exemption
# is silently ignored when the file does not yet exist.
# In the genpack build container (systemd-nspawn + overlayfs), lmdb cannot
# create files due to mmap restrictions on overlayfs, so newaliases cannot
# run at build time either.
# Register as a genpack-init module so newaliases runs before systemd starts,
# before ProtectSystem takes effect, creating aliases.lmdb on first boot.
cp /usr/lib/genpack/genpack-init-postfix.py /usr/lib/genpack-init/postfix.py
