#!/bin/sh
set -e
mkdir -p /etc/greetd
cat << EOF > /etc/greetd/config.toml
[terminal]
vt = 7

[default_session]
command = "tuigreet --user-menu --asterisks"
user = "greetd"
EOF
systemctl enable greetd