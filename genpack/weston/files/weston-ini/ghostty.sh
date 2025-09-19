#!/bin/sh
set -e

mkdir -p /usr/share/icons/hicolor/24x24/apps
vipsthumbnail /usr/share/icons/hicolor/128x128/apps/com.mitchellh.ghostty.png -o /usr/share/icons/hicolor/24x24/apps/com.mitchellh.ghostty.png -s 24x24

sed -i 's|^icon=.*icon_terminal\.png$|icon=/usr/share/icons/hicolor/24x24/apps/com.mitchellh.ghostty.png|' /etc/skel/.config/weston.ini
sed -i 's|^path=.*weston-terminal$|path=/usr/bin/ghostty|' /etc/skel/.config/weston.ini
