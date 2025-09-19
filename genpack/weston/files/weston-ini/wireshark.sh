#!/bin/sh
set -e

# resize  to 24x24
mkdir -p /usr/share/icons/hicolor/24x24/apps
vipsthumbnail /usr/share/icons/hicolor/48x48/apps/wireshark.png -o /usr/share/icons/hicolor/24x24/apps/wireshark.png -s 24x24

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/wireshark.png
path=/usr/bin/wireshark
EOF
