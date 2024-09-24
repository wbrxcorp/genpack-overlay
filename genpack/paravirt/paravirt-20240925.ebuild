EAPI=8

DESCRIPTION="paravirt virtual appliance base"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE=""

RDEPEND="
    genpack/base
    !genpack/systemimg
    app-emulation/qemu-guest-agent
    sys-libs/liburing
    net-misc/socat
"

S="${WORKDIR}"

src_install() {
	# script for genpack
	exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
	doexe "${FILESDIR}/paravirt.sh"
    doexe "${FILESDIR}/qemu-guest-agent.sh"

    insinto /usr/lib/genpack-init
    doins "${FILESDIR}/swapfile.py"
}
