#!/bin/sh
set -e
mkdir -p /usr/share/icons/hicolor/24x24/apps
rsvg-convert -w 24 -h 24 /usr/share/icons/hicolor/scalable/apps/org.gnome.Rhythmbox3.svg -o /usr/share/icons/hicolor/24x24/apps/org.gnome.Rhythmbox3.png
cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/org.gnome.Rhythmbox3.png
path=/usr/bin/rhythmbox
EOF