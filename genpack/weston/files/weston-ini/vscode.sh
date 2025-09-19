#!/bin/sh
set -e

mkdir -p /usr/share/icons/hicolor/24x24/apps
vipsthumbnail /usr/share/pixmaps/vscode.png -o /usr/share/icons/hicolor/24x24/apps/vscode.png -s 24x24

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/vscode.png
path=/usr/bin/code --ozone-platform=wayland --enable-wayland-ime --wayland-text-input-version=1
EOF
