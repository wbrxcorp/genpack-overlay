#!/bin/sh
set -e
#convert svg to 24x24 png
mkdir -p /usr/share/icons/hicolor/24x24
rsvg-convert -w 24 -h 24 -o /usr/share/icons/hicolor/24x24/apps/org.gnome.Nautilus.png /usr/share/icons/hicolor/scalable/apps/org.gnome.Nautilus.svg
cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/org.gnome.Nautilus.png
path=/usr/bin/nautilus
EOF