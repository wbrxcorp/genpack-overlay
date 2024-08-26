EAPI=8

DESCRIPTION="paravirt virtual appliance base"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+btrfs +xfs +wireguard"

RDEPEND="
    sys-kernel/paravirt-kernel
    app-emulation/qemu-guest-agent
    sys-libs/liburing
    app-editors/nano
    app-editors/vim
    dev-debug/strace
    wireguard? ( net-vpn/wireguard-tools )
    btrfs? ( sys-fs/btrfs-progs )
    xfs? ( sys-fs/xfsprogs )
"

S="${WORKDIR}"

src_install() {
	# proxy init
	exeinto /usr/bin
	doexe "${FILESDIR}/paravirt-init"

	keepdir /usr/lib/genpack-init

	# script for genpack
	exeinto /usr/lib/genpack/package-scripts
	doexe "${FILESDIR}/paravirt.sh"
}
