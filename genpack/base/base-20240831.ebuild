EAPI=8

DESCRIPTION="base system"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+vi +strace +btrfs +xfs +wireguard +cron +audit +logrotate +sshd +tcpdump"

REQUIRED_USE="
    logrotate? ( cron )
"

RDEPEND="
    sys-kernel/genpack-kernel
    sys-apps/genpack-init
    sys-apps/gentoo-systemd-integration
    sys-libs/timezone-data
    app-shells/bash
    sys-apps/net-tools
    app-arch/gzip
    dev-lang/python
    sys-apps/grep
    app-misc/ca-certificates
    sys-apps/coreutils
    sys-process/procps
    net-misc/rsync
    net-misc/iputils
    sys-apps/iproute2
    tcpdump? ( net-analyzer/tcpdump )
    sshd? ( net-misc/openssh )
    vi? ( app-editors/vim )
    strace? ( dev-debug/strace )
    wireguard? ( net-vpn/wireguard-tools )
    btrfs? ( sys-fs/btrfs-progs )
    xfs? ( sys-fs/xfsprogs )
    cron? ( sys-process/cronie )
    audit? ( sys-process/audit )
    logrotate? ( app-admin/logrotate )
"

S="${WORKDIR}"

src_install() {
	# script for genpack

    exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
	doexe "${FILESDIR}/kernel-install.py"
    doexe "${FILESDIR}/copyup-fundamentals.sh"

    if use cron; then
        doexe "${FILESDIR}/cron.sh"
    fi
    if use audit; then
        doexe "${FILESDIR}/audit.sh"
    fi
    if use sshd; then
        doexe "${FILESDIR}/sshd.sh"
    fi
}
