EAPI=8
inherit git-r3

DESCRIPTION="Library for wireguard hub infrastructure"
HOMEPAGE="https://github.com/shimarin/wghub"
EGIT_REPO_URI="https://github.com/shimarin/wghub.git"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

DEPEND="dev-cpp/argparse dev-cpp/nlohmann_json"
RDEPEND="dev-libs/openssl net-misc/curl dev-libs/iniparser"

pkg_setup() {
    export EGIT_COMMIT_DATE="$(echo ${PV} | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')"
    einfo "EGIT_COMMIT_DATE set to ${EGIT_COMMIT_DATE}"
}

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" install || die "emake install failed"
}
