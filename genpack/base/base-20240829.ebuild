EAPI=8

DESCRIPTION="base system"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+vi +strace +btrfs +xfs +wireguard +cron +audit +logrotate"

REQUIRED_USE="
    logrotate? ( cron )
"

RDEPEND="
    sys-kernel/genpack-kernel
    sys-apps/genpack-init
    app-editors/nano
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
	exeinto /usr/lib/genpack/package-scripts
    use cron && doexe "${FILESDIR}/cron.sh"
    use audit && doexe "${FILESDIR}/audit.sh"
}
