#!/bin/sh
set -e
systemctl enable cleanup-boottimetxt.service
if [ ! -f /etc/hostname ]; then
        echo -n "$ARTIFACT" > /etc/hostname
fi
if [ ! -f /boot/grub/grub.cfg ]; then
	mkdir -p /boot/grub
	cp /usr/lib/genpack/systemimg/grub.cfg /boot/grub/
fi
