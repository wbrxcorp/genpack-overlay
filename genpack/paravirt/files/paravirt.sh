#!/bin/sh
set -e
if [ ! -f /etc/hostname ]; then
	echo -n "$ARTIFACT" > /etc/hostname
fi
if [ ! -f /etc/vconsole.conf ]; then
	echo 'KEYMAP=@kernel' > /etc/vconsole.conf
fi