#!/bin/sh
[ "${root%%:*}" = "block" ] || exit 0

RO=${root#block:}

udevadm settle

if [ ! -b "$RO" ]; then
	timeout=$(getargnum 5 1 180 rd.timeout)
	info "Waiting for RO layer $RO to be recognized by system(max $timeout sec)..."
	sleep 1
	while [ ! -b "$RO" ] && [ "$timeout" -gt 0 ]; do
		sleep 1
		timeout=$((timeout - 1))
	done
fi

[ -e /run/initramfs/ro ] || mkdir -m 0755 -p /run/initramfs/ro
mount -o ro -t squashfs "$RO" /run/initramfs/ro || die "Failed to mount RO layer"

[ -e /run/initramfs/rw ] || mkdir -m 0755 -p /run/initramfs/rw
mount -t tmpfs tmpfs /run/initramfs/rw || die "Failed to mount tmpfs as RW layer"

[ -e /run/initramfs/rw/root ] || mkdir -m 0755 -p /run/initramfs/rw/root
[ -e /run/initramfs/rw/work ] || mkdir -m 0755 -p /run/initramfs/rw/work

mount -t overlay overlay -o lowerdir=/run/initramfs/ro,upperdir=/run/initramfs/rw/root,workdir=/run/initramfs/rw/work $NEWROOT || die "Failed to mount overlay root"
