#!/bin/sh

udevadm settle

if [ ! -b "$root" ]; then
	timeout=$(getargnum 5 1 180 rd.timeout)
	info "Waiting for boot partition to be recognized by system(max $timeout sec)..."
	sleep 1
	while [ ! -b "$root" ] && [ "$timeout" -gt 0 ]; do
		sleep 1
		timeout=$((timeout - 1))
	done
fi

[ -e /run/initramfs/ro ] || mkdir -m 0755 -p /run/initramfs/ro
mount -o ro -t squashfs "$root" /run/initramfs/ro || die "Failed to mount RO layer"

[ -e /run/initramfs/rw ] || mkdir -m 0755 -p /run/initramfs/rw
if ! getargbool 0 paravirt.transient; then
	mount -t auto /dev/vdb /run/initramfs/rw
	if ! ismounted /run/initramfs/rw; then
		info "RW layer not mounted.  Proceeding with virtiofs"
		mount -t virtiofs fs /run/initramfs/rw
	fi
fi

if ! ismounted /run/initramfs/rw; then
	info "RW Layer not mounted.  Proceeding with tmpfs"
	mount -t tmpfs tmpfs /run/initramfs/rw || die "Failed to mount tmpfs as RW layer"
fi

[ -e /run/initramfs/rw/root ] || mkdir -m 0755 -p /run/initramfs/rw/root
[ -e /run/initramfs/rw/work ] || mkdir -m 0755 -p /run/initramfs/rw/work

mount -t overlay overlay -o lowerdir=/run/initramfs/ro,upperdir=/run/initramfs/rw/root,workdir=/run/initramfs/rw/work $NEWROOT || die "Failed to mount overlay root"
