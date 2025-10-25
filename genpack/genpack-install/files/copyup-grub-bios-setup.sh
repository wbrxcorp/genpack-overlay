#!/bin/sh
set -e
if [ -x /usr/bin/grub-bios-setup ]; then
    recursive-touch /usr/bin/grub-bios-setup
fi
