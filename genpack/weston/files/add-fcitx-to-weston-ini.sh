#!/bin/sh
set -e

mkdir -p /etc/skel/.config
cat << EOF >> /etc/skel/.config/weston.ini
[input-method]
path=/usr/libexec/fcitx5-wayland-launcher
EOF
