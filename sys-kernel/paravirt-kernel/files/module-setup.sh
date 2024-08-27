#!/bin/bash

check() {
    require_kernel_modules virtio_blk btrfs xfs squashfs loop overlay || return 1
    return 255
}

depends() {
    echo base
}

installkernel() {
    hostonly="" instmods virtio_blk btrfs xfs squashfs loop overlay
}

install() {
    if [[ $genpack_transient ]]; then
        inst_hook mount 01 "$moddir/mount-paravirt-transient.sh"    # overlay tmpfs on top of block device
    else
        inst_hook mount 01 "$moddir/mount-paravirt.sh"     # overlay on top of block device
    fi
}
