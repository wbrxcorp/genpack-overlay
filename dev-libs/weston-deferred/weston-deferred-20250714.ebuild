EAPI=8
inherit git-r3

DESCRIPTION="Defer launching Weston until a physical display is detected"
HOMEPAGE="https://github.com/wbrxcorp/weston-deferred"
EGIT_REPO_URI="https://github.com/wbrxcorp/weston-deferred.git"
EGIT_COMMIT="00100aab0ec11ca29275f43873e70564509e0c27"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

RDEPEND="
	sys-apps/systemd
	dev-libs/weston
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}
