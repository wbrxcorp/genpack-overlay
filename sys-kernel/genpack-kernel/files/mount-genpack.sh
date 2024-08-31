#!/bin/sh

# transient=1

udevadm settle

if [ "${root%%:*}" = "systemimg" ]; then
	UUID=${root#systemimg:}
	info "Boot partition UUID=$UUID"

	SYSTEMIMG_BOOT_PARTITION="$(label_uuid_to_dev UUID=$UUID)"
	DATA_PARTITION="$(label_uuid_to_dev LABEL=data-$UUID)"

	if [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ]; then
		timeout=$(getargnum 5 1 180 rd.timeout)
		info "Waiting for boot partition to be recognized by system(max $timeout sec)..."
		sleep 1
		while [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ] && [ "$timeout" -gt 0 ]; do
			sleep 1
			timeout=$((timeout - 1))
		done
		if [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ]; then
			info "Timeout. assuming that /dev/sda1 is a boot partition and /dev/sda2 is a data partition"
			SYSTEMIMG_BOOT_PARTITION="/dev/sda1"
			DATA_PARTITION="/dev/sda2"
		fi
	fi

	[ -e /run/initramfs/boot ] || mkdir -m 0755 -p /run/initramfs/boot
	eval $(blkid  -o udev -s TYPE "$SYSTEMIMG_BOOT_PARTITION")
	if [ "$ID_FS_TYPE" == "vfat" ]; then
		/usr/bin/fsck.fat -aw "$SYSTEMIMG_BOOT_PARTITION"
		mount -t vfat "$SYSTEMIMG_BOOT_PARTITION" /run/initramfs/boot || die "Failed to mount boot partition(FAT)"
		if [ -f /run/initramfs/boot/system.cur ]; then
			info "Found system.cur.  Renaming it to system.old"
			mv /run/initramfs/boot/system.cur /run/initramfs/boot/system.old
		fi
		/usr/bin/date > /run/initramfs/boot/boottime.txt || info "creating boottime.txt failed"
	else
		mount -t auto -o ro "$SYSTEMIMG_BOOT_PARTITION" /run/initramfs/boot || die "Failed to mount boot partition(readonly)"
	fi
	GENPACK_IMAGE="/run/initramfs/boot/system.img"
elif [ "${root%%:*}" = "block" ]; then
	GENPACK_IMAGE="/dev/vda"
	DATA_PARTITION="/dev/vdb"
else
	exit 0 # unknown root= type
fi

[ -e /run/initramfs/ro ] || mkdir -m 0755 -p /run/initramfs/ro
mount -o ro -t squashfs "$GENPACK_IMAGE" /run/initramfs/ro || die "Failed to mount RO layer"

[ -e /run/initramfs/rw ] || mkdir -m 0755 -p /run/initramfs/rw
if getargbool 0 genpack.transient || [[ $transient ]]; then
	info "Transient mode. skipping data partition mount"
else
	# try data partition first, then virtiofs
	mount -t auto "$DATA_PARTITION" /run/initramfs/rw || mount -t virtiofs fs /run/initramfs/rw
fi

if ! ismounted /run/initramfs/rw; then
	info "Data partition not mounted.  Proceeding with tmpfs"
	mount -t tmpfs tmpfs /run/initramfs/rw || die "Failed to mount tmpfs as data partition"
fi

GENPACK_OVERLAY_ROOT="/run/initramfs/rw/root"
GENPACK_OVERLAY_WORK="/run/initramfs/rw/work"

# if old structure found, mount it instead
if [ -d /run/initramfs/rw/rw/root ]; then
	info "Old structure found.  Mounting it instead"
	GENPACK_OVERLAY_ROOT="/run/initramfs/rw/rw/root"
	GENPACK_OVERLAY_WORK="/run/initramfs/rw/rw/work"
fi

[ -e "$GENPACK_OVERLAY_ROOT" ] || mkdir -m 0755 -p $GENPACK_OVERLAY_ROOT
[ -e "$GENPACK_OVERLAY_WORK" ] || mkdir -m 0755 -p $GENPACK_OVERLAY_WORK

mount -t overlay overlay -o lowerdir=/run/initramfs/ro,upperdir=$GENPACK_OVERLAY_ROOT,workdir=$GENPACK_OVERLAY_WORK $NEWROOT || die "Failed to mount overlay root"
