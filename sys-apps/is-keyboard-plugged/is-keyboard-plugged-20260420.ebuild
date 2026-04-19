EAPI=8

inherit git-r3

DESCRIPTION="Detect whether a USB keyboard is connected"
HOMEPAGE="https://github.com/shimarin/is-keyboard-plugged"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/is-keyboard-plugged.git"
EGIT_COMMIT="ce344e0c0dec5fe36af46f54294e74f8e6168e84"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

src_install() {
	emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}
