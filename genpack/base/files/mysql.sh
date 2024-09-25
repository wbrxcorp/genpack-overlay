#!/bin/sh
set -e
recursive-touch /var/log/mysql

sed -i 's/^log-bin$/disable-log-bin/' /etc/mysql/mysql.d/50-distro-server.cnf

mkdir -p /usr/lib/genpack-init
cp /usr/lib/genpack/genpack-init-mysql.py /usr/lib/genpack-init/