#!/bin/sh
set -e

cat << EOF >> /etc/skel/.config/weston.ini
[launcher]
icon=/usr/share/icons/hicolor/24x24/apps/google-chrome.png
path=/usr/bin/google-chrome-stable --enable-wayland-ime --wayland-text-input-version=1 --no-first-run --no-default-browser-check --disable-first-run-ui
EOF
