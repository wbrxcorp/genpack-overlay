#!/bin/sh
set -e
mkdir -p /usr/share/icons/hicolor/24x24/apps
rsvg-convert -w 24 -h 24 -o /usr/share/icons/hicolor/24x24/apps/org.gnome.TextEditor.png /usr/share/icons/hicolor/scalable/apps/org.gnome.TextEditor.svg

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/org.gnome.TextEditor.png
path=/usr/bin/gnome-text-editor
EOF
