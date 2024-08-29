EAPI=8

DESCRIPTION="paravirt virtual appliance base"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+btrfs +xfs +wireguard +cron +audit"

RDEPEND="
    genpack/base
    !genpack/systemimg
    sys-kernel/genpack-kernel
    sys-apps/genpack-init
    app-emulation/qemu-guest-agent
    sys-libs/liburing
"

S="${WORKDIR}"

src_install() {
	# script for genpack
	exeinto /usr/lib/genpack/package-scripts
	doexe "${FILESDIR}/paravirt.sh"
    use cron && doexe "${FILESDIR}/cron.sh"
    use audit && doexe "${FILESDIR}/audit.sh"
}
