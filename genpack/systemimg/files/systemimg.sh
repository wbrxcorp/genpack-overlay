#!/bin/sh
set -e
#systemctl enable cleanup-boottimetxt.service # moved to initramfs shutdown
if [ ! -f /etc/hostname ]; then
        echo -n "$ARTIFACT" > /etc/hostname
fi
#new bootloader does not need this
#if [ ! -f /boot/grub/grub.cfg ]; then
#	mkdir -p /boot/grub
#	cp /usr/lib/genpack/systemimg/grub.cfg /boot/grub/
#fi
