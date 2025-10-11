EAPI=8

DESCRIPTION="development packages"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

IUSE=""

RDEPEND="
    sys-devel/gcc
    dev-debug/gdb
"

S="${WORKDIR}"

src_install() {
    exeinto /usr/bin
    newexe ${FILESDIR}/genpack-devel genpack-devel
}
