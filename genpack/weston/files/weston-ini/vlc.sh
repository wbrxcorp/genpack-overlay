#!/bin/sh
set -e
#resize 48x48 icon to 24x24 using vipsthumbnail
mkdir -p /usr/share/icons/hicolor/24x24/apps
vipsthumbnail /usr/share/icons/hicolor/48x48/apps/vlc.png -s 24x24 -o /usr/share/icons/hicolor/24x24/apps/vlc.png
cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/vlc.png
path=/usr/bin/vlc
EOF