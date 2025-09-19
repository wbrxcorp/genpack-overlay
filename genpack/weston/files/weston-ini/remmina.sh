#!/bin/sh
set -e

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/org.remmina.Remmina.png
path=/usr/bin/remmina
EOF