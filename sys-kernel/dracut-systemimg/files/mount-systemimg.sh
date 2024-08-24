#!/bin/sh

[ "${root%%:*}" = "systemimg" ] || exit 0

udevsettle

UUID=${root#systemimg:}

info "Boot partition UUID=$UUID"

SYSTEMIMG_BOOT_PARTITION="$(label_uuid_to_dev UUID=$UUID)"
SYSTEMIMG_DATA_PARTITION="$(label_uuid_to_dev LABEL=data-$UUID)"

[ -e /run/initramfs/boot ] || mkdir -m 0755 -p /run/initramfs/boot
eval $(blkid  -o udev -s TYPE "$SYSTEMIMG_BOOT_PARTITION")
if [ "$ID_FS_TYPE" == "vfat" ]; then
       /usr/bin/fsck.fat -aw "$SYSTEMIMG_BOOT_PARTITION"
       mount -t vfat "$SYSTEMIMG_BOOT_PARTITION" /run/initramfs/boot || die "Failed to mount boot partition(FAT)"
       /usr/bin/date > /run/initramfs/boot/boottime.txt || info "creating boottime.txt failed"
else
       mount -t auto -o ro "$SYSTEMIMG_BOOT_PARTITION" /run/initramfs/boot || die "Failed to mount boot partition(readonly)"
fi

[ -e /run/initramfs/ro ] || mkdir -m 0755 -p /run/initramfs/ro
mount -o loop,ro -t squashfs /run/initramfs/boot/system.img /run/initramfs/ro || die "Failed to loopback mount system.img"

[ -e /run/initramfs/rw ] || mkdir -m 0755 -p /run/initramfs/rw
getargbool 0 systemimg.transient || mount -t auto "$SYSTEMIMG_DATA_PARTITION" /run/initramfs/rw
if ! ismounted /run/initramfs/rw; then
    info "Data partition not mounted.  Proceeding with tmpfs"
    mount -t tmpfs tmpfs /run/initramfs/rw || die "Failed to mount tmpfs as data partition"
fi

[ -e /run/initramfs/rw/root ] || mkdir -m 0755 -p /run/initramfs/rw/root
[ -e /run/initramfs/rw/work ] || mkdir -m 0755 -p /run/initramfs/rw/work

mount -t overlay overlay -o lowerdir=/run/initramfs/ro,upperdir=/run/initramfs/rw/root,workdir=/run/initramfs/rw/work $NEWROOT || die "Failed to mount overlay root"
