EAPI=8

DESCRIPTION="base system"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+vi +strace +btrfs +xfs +wireguard +cron +audit +logrotate +sshd +tcpdump +banner"

REQUIRED_USE="
    logrotate? ( cron )
"

RDEPEND="
    || ( sys-kernel/gentoo-kernel[initramfs] sys-kernel/gentoo-kernel-bin[initramfs] )
    sys-kernel/dracut-genpack
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

    use cron && doexe "${FILESDIR}/cron.sh"
    use audit && doexe "${FILESDIR}/audit.sh"
    use sshd && doexe "${FILESDIR}/sshd.sh"
    use banner && doexe "${FILESDIR}/generate-default-banner.sh"

    exeinto /usr/lib/genpack/package-scripts/sys-apps/systemd
    doexe "${FILESDIR}/systemd.sh"

    exeinto /usr/lib/genpack/package-scripts/net-firewall/iptables
    doexe "${FILESDIR}/iptables-set-legacy.sh"

    exeinto /usr/bin
    newexe "${FILESDIR}/glsa-check.py" genpack-glsa-check

    insinto /usr/lib/genpack-init
    use banner && doins "${FILESDIR}/01banner.py"
}
