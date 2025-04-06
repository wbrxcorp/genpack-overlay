#!/bin/sh
set -e
sed -i 's/^#en_US ISO-8859-1/en_US ISO-8859-1/g' /etc/locale.gen
sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen
sed -i 's/^#ja_JP.UTF-8/ja_JP.UTF-8/g' /etc/locale.gen
locale-gen
