#!/bin/sh
set -e
PGSQL_VERSION=$(eselect postgresql show)
emerge --config dev-db/postgresql # setup initial database
eselect postgresql set $PGSQL_VERSION # create symlinks

ln -s postgresql-$PGSQL_VERSION.service /usr/lib/systemd/system/postgresql.service
ln -s postgresql-$PGSQL_VERSION /etc/postgresql
