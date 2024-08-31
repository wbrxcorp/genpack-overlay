EAPI=8

inherit genpack-ignore

DESCRIPTION="boot time banner generator"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE=""

RDEPEND="app-misc/figlet"

S="${WORKDIR}"

src_install() {
    exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
	doexe "${FILESDIR}/generate-default-banner.sh"
}
