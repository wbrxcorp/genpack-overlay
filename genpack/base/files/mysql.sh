#!/bin/sh
set -e
recursive-touch /var/log/mysql

SERVER_CONF=/etc/mysql/mysql.d/50-distro-server.cnf
sed -i 's/^log-bin$/disable-log-bin/' $SERVER_CONF
echo 'plugin-load-add=auth_socket.so' >> $SERVER_CONF

if [ ! -d /var/lib/mysql/mysql -a -x /usr/sbin/mysqld ]; then
    # Initialize MySQL data directory
    # with-mysql is a part of genpack-progs
    with-mysql "mysql --mysql-plugin=auth_socket.so -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH auth_socket\""
fi

mkdir -p /usr/lib/genpack-init
cp /usr/lib/genpack/genpack-init-mysql.py /usr/lib/genpack-init/