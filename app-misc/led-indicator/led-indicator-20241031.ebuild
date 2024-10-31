EAPI=8
inherit git-r3

DESCRIPTION="Simple LED indicator service"
HOMEPAGE="https://github.com/shimarin/led-indicator"
EGIT_REPO_URI="https://github.com/shimarin/led-indicator.git"
EGIT_COMMIT="20a8a5b0ec9c603fa1320b4d6e436241ea7e1526"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

DEPEND="dev-cpp/argparse"
RDEPEND="
	dev-libs/libgpiod[cxx]
	<dev-cpp/sdbus-c++-2
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}

