#!/bin/sh
set -e

cat << EOF >> /etc/skel/.config/weston.ini
[input-method]
path=/usr/libexec/fcitx5-wayland-launcher
EOF
