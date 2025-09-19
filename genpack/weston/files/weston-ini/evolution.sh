#!/bin/sh
set -e

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/evolution-mail.png
path=/usr/bin/evolution
EOF
