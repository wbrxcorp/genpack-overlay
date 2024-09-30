#!/bin/sh
set -e

# generate default ssl certs (somwhow it needs to be executed twice)
ebuild /var/db/pkg/www-servers/apache-*/apache-*.ebuild postinst
ebuild /var/db/pkg/www-servers/apache-*/apache-*.ebuild postinst

sed -i 's/^\(APACHE2_OPTS=.*\)\"$/\1 -D PROXY -D DAV"/' /etc/conf.d/apache2
