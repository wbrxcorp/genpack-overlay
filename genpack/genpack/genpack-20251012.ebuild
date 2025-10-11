EAPI=8

PYTHON_COMPAT=( python3_{12..13} )
inherit python-single-r1 git-r3

DESCRIPTION="OS image builder based on Gentoo Linux"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack.git"
EGIT_COMMIT="cbb4532a97595a02a83318c0ec1b1f4fbff22a38"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

BDEPEND="
    dev-cpp/argparse
"

RDEPEND="
    dev-python/json5
    dev-python/requests
"

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}