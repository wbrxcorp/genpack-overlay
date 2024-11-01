EAPI=8
inherit git-r3

DESCRIPTION="Generate WireGuard client configuration file"
HOMEPAGE="https://github.com/shimarin/wg-genconf"
EGIT_REPO_URI="https://github.com/shimarin/wg-genconf.git"
EGIT_COMMIT="549b21668465bd5ca7a60fc9fc4b6a4ddf9af89f"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

DEPEND="dev-cpp/argparse"
RDEPEND="
	dev-libs/openssl
"

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}

