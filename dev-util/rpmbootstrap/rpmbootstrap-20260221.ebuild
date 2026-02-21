EAPI=8
inherit git-r3

DESCRIPTION="Bootstrap RPM-based Linux distribution"
HOMEPAGE="https://github.com/shimarin/rpmbootstrap"
EGIT_REPO_URI="https://github.com/shimarin/rpmbootstrap.git"
EGIT_COMMIT="fc8d13dda49ff5e5642d668cdd8eee00548724ec"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="dev-libs/libxml2 net-misc/curl app-arch/rpm[caps] app-arch/gzip app-arch/zstd"
DEPEND="${RDEPEND} dev-cpp/argparse"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" install || die "emake install failed"
}

