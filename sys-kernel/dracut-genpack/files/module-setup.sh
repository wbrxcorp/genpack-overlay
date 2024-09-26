#!/bin/bash

check() {
    require_kernel_modules btrfs xfs squashfs loop overlay || return 1
    return 255
}

depends() {
    echo base
}

installkernel() {
    hostonly="" instmods virtiofs virtio_blk btrfs xfs squashfs loop overlay
}

install() {
    inst_binary /usr/bin/date
    inst_binary /usr/bin/fsck.fat
    inst_hook cmdline 30 "$moddir/check-systemimg-root.sh"
    inst_hook mount 01 "$moddir/mount-genpack.sh"     # overlay on top of block device
}
