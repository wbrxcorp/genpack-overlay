#!/bin/sh
# Package script for dev-db/mysql. genpack-exec-package-scripts runs this as
# the first step of the upper build, on the upper overlay, before artifact
# scripts (see genpack.py upper(): "execute package scripts and generate
# metadata (must run before artifact scripts)").
#
# /var/lib/mysql is not in the CONTENTS of dev-db/mysql. genpack-copyup only
# copy-ups files listed in runtime package CONTENTS plus a few extra top-level
# paths (/bin /sbin /lib /lib64 /usr/sbin /run /proc /sys /root /home /tmp
# /mnt). The final squashfs is packed from the upper layer alone, so a datadir
# that exists only in the lower layer never reaches the image. This script
# must therefore create a fresh datadir here in the upper phase.
#
# Lower phase must not initialize the datadir. In particular do not run
# `emerge --config dev-db/mysql` (pkg_config runs mysqld --initialize-insecure
# and dies if already initialized) or with-mysql against the lower image.
# with-mysql itself initializes only when <datadir>/mysql is absent, and
# silently skips otherwise — which is how a contaminated lower layer used to
# pass the build with an incomplete datadir in the image.
set -e

if [ -d /var/lib/mysql/mysql ]; then
	echo "mysql.sh: initialized MySQL datadir already exists at /var/lib/mysql/mysql" >&2
	echo "This is a build-time error: /var/lib/mysql is not a package file, so genpack-copyup will not copy it from the lower layer into the upper overlay. The final image (squashfs packed from upper only) would then lack mysql/, sys/, performance_schema/, auto.cnf, certificates, etc., and mysqld would fail to start ('System schema directory does not exist')." >&2
	echo "Likely cause: with-mysql or 'emerge --config dev-db/mysql' was run against the lower layer." >&2
	echo "Fix: wipe the lower-image datadir (rm -rf /var/lib/mysql) and rebuild; do not initialize MySQL during the lower phase." >&2
	exit 1
fi

recursive-touch /var/log/mysql

SERVER_CONF=/etc/mysql/mysql.d/50-distro-server.cnf
sed -i 's/^log-bin$/disable-log-bin/' $SERVER_CONF
grep -q '^plugin-load-add=auth_socket.so$' $SERVER_CONF || echo 'plugin-load-add=auth_socket.so' >> $SERVER_CONF

if [ -x /usr/sbin/mysqld ]; then
	# with-mysql is a part of genpack-progs
	with-mysql --mysql-plugin=auth_socket.so "mysql -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH auth_socket\""
fi

mkdir -p /usr/lib/genpack-init
cp /usr/lib/genpack/genpack-init-mysql.py /usr/lib/genpack-init/
