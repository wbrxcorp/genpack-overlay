EAPI=8
inherit git-r3

DESCRIPTION="Automatically restart dead WireGuard interfaces"
HOMEPAGE="https://github.com/shimarin/wg-keepalive"
EGIT_REPO_URI="https://github.com/shimarin/wg-keepalive.git"
EGIT_COMMIT="8af5af9b85489754a0eab3735fc12bd998453f4d"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

DEPEND="dev-cpp/argparse"
RDEPEND="
	dev-libs/iniparser dev-libs/spdlog net-vpn/wireguard-tools
"

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}

