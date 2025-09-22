#!/bin/sh
set -e
mkdir -p /usr/share/icons/hicolor/24x24/apps
rsvg-convert -w 24 -h 24 -o /usr/share/icons/hicolor/24x24/apps/org.gnome.seahorse.Application.png /usr/share/icons/hicolor/scalable/apps/org.gnome.seahorse.Application.svg
mkdir -p /etc/skel/.config
cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/org.gnome.seahorse.Application.png
path=/usr/bin/seahorse
EOF