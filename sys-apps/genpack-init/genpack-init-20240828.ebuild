EAPI=8

DESCRIPTION="intermediate init for genpack system"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND=""

S="${WORKDIR}"

src_install() {
	exeinto /usr/bin
	doexe "${FILESDIR}/genpack-init"

	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/99default_network_interface.py"

	dodir /usr/lib/dracut/dracut.conf.d
	echo 'realinitpath="/usr/bin/genpack-init"' > "${D}/usr/lib/dracut/dracut.conf.d/realinitpath.conf"
}

