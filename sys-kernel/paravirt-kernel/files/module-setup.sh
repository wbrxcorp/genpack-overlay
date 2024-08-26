#!/bin/bash

check() {
    require_kernel_modules btrfs xfs squashfs loop overlay || return 1
    return 255
}

depends() {
    echo base
}

installkernel() {
    hostonly="" instmods btrfs xfs squashfs loop overlay
}

install() {
    inst_hook mount 01 "$moddir/mount-paravirt.sh"     # overlay on top of block device
}
