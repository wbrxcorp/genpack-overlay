#!/bin/sh
mkdir -p /etc/skel/.config
cat <<EOF >>/etc/skel/.config/weston.ini
#[autolaunch]
#path=/usr/bin/weston-init
EOF
