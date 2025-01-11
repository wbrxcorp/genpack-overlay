EAPI=8
inherit git-r3

DESCRIPTION="Library for wireguard hub infrastructure"
HOMEPAGE="https://github.com/shimarin/wghub"
EGIT_REPO_URI="https://github.com/shimarin/wghub.git"
EGIT_COMMIT="d11274b"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

DEPEND="dev-cpp/argparse dev-cpp/nlohmann_json"
RDEPEND="dev-libs/openssl net-misc/curl >=dev-libs/iniparser-4.2.5"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}
