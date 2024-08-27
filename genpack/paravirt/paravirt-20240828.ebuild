EAPI=8

DESCRIPTION="paravirt virtual appliance base"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+btrfs +xfs +wireguard"

RDEPEND="
    !genpack/systemimg
    sys-kernel/paravirt-kernel
    sys-apps/genpack-init
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
	# script for genpack
	exeinto /usr/lib/genpack/package-scripts
	doexe "${FILESDIR}/paravirt.sh"
}
