EAPI=8
inherit git-r3

DESCRIPTION="Bootstrap RPM-based Linux distribution"
HOMEPAGE="https://github.com/shimarin/rpmbootstrap"
EGIT_REPO_URI="https://github.com/shimarin/rpmbootstrap.git"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="dev-libs/libxml2 net-misc/curl app-arch/rpm[caps]"
DEPEND="${RDEPEND} dev-cpp/argparse"

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

