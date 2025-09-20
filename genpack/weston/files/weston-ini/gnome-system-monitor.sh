#!/bin/sh
set -e

mkdir -p /usr/share/icons/hicolor/24x24/apps
rsvg-convert -w 24 -h 24 -o /usr/share/icons/hicolor/24x24/apps/org.gnome.SystemMonitor.png /usr/share/icons/hicolor/scalable/apps/org.gnome.SystemMonitor.svg

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/org.gnome.SystemMonitor.png
path=/usr/bin/gnome-system-monitor
EOF
