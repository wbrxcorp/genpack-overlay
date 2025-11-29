#!/bin/sh
set -e
eselect php set cli $(eselect php show cli)

if [ -f /etc/apache2/modules.d/70_mod_php.conf ]; then
    eselect php set apache2 $(eselect php show apache2)
fi

if [ -f /usr/libexec/php-fpm-launcher ]; then
    eselect php set fpm $(eselect php show fpm)
fi
