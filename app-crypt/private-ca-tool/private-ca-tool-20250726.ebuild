EAPI=8

PYTHON_COMPAT=( python3_{13..15} )
inherit python-single-r1

DESCRIPTION="Tool for managing a private CA"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

RDEPEND="dev-libs/openssl　dev-libs/nss"

S="${WORKDIR}"

src_install() {
    exeinto /usr/bin
    doexe "${FILESDIR}/private-ca-tool.py"
    mv "${D}/usr/bin/private-ca-tool.py" "${D}/usr/bin/private-ca-tool"
}
