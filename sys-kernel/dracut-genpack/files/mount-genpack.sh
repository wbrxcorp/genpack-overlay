#!/bin/sh

# transient=1

udevadm settle

if [ "${root%%:*}" = "systemimg" ]; then
	UUID=${root#systemimg:}
	if [ "$UUID" = "auto" ]; then
		info "Auto-detecting boot partition"
		# enum all vfat partitions and find the one with /system.img
		mkdir -p /mnt/systemimg-tmp-mount
		for i in $(blkid -t TYPE=vfat -o device); do
			mount -o ro -t vfat $i /mnt/systemimg-tmp-mount || continue
			file_exists=$( [ -f /mnt/systemimg-tmp-mount/system.img ] && echo 1 || echo 0 )
			umount /mnt/systemimg-tmp-mount
			[ "$file_exists" = "1" ] || continue
			#else
			if [ "$UUID" != "auto" ]; then
				info "Warning: Multiple boot partitions found.  Using the first one"
				break
			fi
			UUID=$(blkid -o value -s UUID "$i")
			info "Found boot partition $i"
		done

		if [ "$UUID" = "auto" ]; then
			die "Failed to find boot partition"
		fi
	fi

	info "Boot partition UUID=$UUID"

	SYSTEMIMG_BOOT_PARTITION="$(label_uuid_to_dev UUID=$UUID)"

	if [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ]; then
		timeout=$(getargnum 15 1 180 rd.timeout)
		info "Waiting for boot partition to be recognized by system(max $timeout sec)..."
		sleep 1
		while [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ] && [ "$timeout" -gt 0 ]; do
			sleep 1
			timeout=$((timeout - 1))
		done
		if [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ]; then
			info "Timeout.  Trying to find boot partition by TYPE=vfat"
			SYSTEMIMG_BOOT_PARTITION=$(blkid -t TYPE=vfat -o device | head -1)
			if [ ! -b "$SYSTEMIMG_BOOT_PARTITION" ]; then
				die "Failed to find boot partition"
			fi
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

	for i in "data-" "d-" "wbdata-"; do
		DATA_PARTITION="$(label_uuid_to_dev LABEL=$i$UUID)"
		[ -b "$DATA_PARTITION" ] && break
	done
	if [ ! -b "$DATA_PARTITION" ]; then
		[ -L "$SYSTEMIMG_BOOT_PARTITION" ] && SYSTEMIMG_BOOT_PARTITION=$(blkid -U $UUID)
		# replace last "1" with "2"
		DATA_PARTITION="${SYSTEMIMG_BOOT_PARTITION%?}2"
	fi
elif [ "${root%%:*}" = "block" ]; then
	GENPACK_IMAGE="/dev/vda"
	DATA_PARTITION="/dev/vdb"
else
	exit 0 # unknown root= type
fi

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

[ -e /run/initramfs/ro ] || mkdir -m 0755 -p /run/initramfs/ro

if [ ! -e "$GENPACK_IMAGE" ]; then
	if [ -f /run/initramfs/rw/system ]; then
		info "system.img not found in boot partition.  Using one from data partition instead"
		GENPACK_IMAGE="/run/initramfs/rw/system"
		if [ -f /run/initramfs/rw/system.cur ]; then
			info "Found system.cur in data partition.  Renaming it to system.old"
			mv /run/initramfs/rw/system.cur /run/initramfs/rw/system.old
		fi
	else
		die "genpack image not found: $GENPACK_IMAGE"
	fi
fi

mount -o ro -t squashfs "$GENPACK_IMAGE" /run/initramfs/ro || die "Failed to mount RO layer"

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

# if /usr exists in rw, its timestamp must be same as ro's corresponding one
# because systemd considers /usr's timestamp as the distribution's timestamp
GENPACK_RW_USR="$GENPACK_OVERLAY_ROOT"/usr
if [ -e /run/initramfs/ro/usr -a -e "$GENPACK_RW_USR" ]; then
	/usr/bin/touch -r /run/initramfs/ro/usr $GENPACK_RW_USR
fi

# install shutdown program
mount -o remount,exec /run
if [ -x /run/initramfs/ro/usr/libexec/genpack-shutdown ]; then
        cp -a /run/initramfs/ro/usr/libexec/genpack-shutdown /run/initramfs/shutdown
fi

mount -t overlay overlay -o lowerdir=/run/initramfs/ro,upperdir=$GENPACK_OVERLAY_ROOT,workdir=$GENPACK_OVERLAY_WORK $NEWROOT || die "Failed to mount overlay root"
