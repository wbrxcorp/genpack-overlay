EAPI=8
inherit git-r3

DESCRIPTION="Walbrix admin UI"
HOMEPAGE="https://github.com/wbrxcorp/wbui"
EGIT_REPO_URI="https://github.com/wbrxcorp/wbui.git"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="
    app-admin/wb
    dev-libs/weston[systemd,kiosk]
    dev-python/wheel
    gui-libs/gtk[wayland,introspection]
    dev-util/wayland-scanner
    dev-python/pygobject
    dev-python/python-pam
    media-fonts/vlgothic
    media-fonts/noto-emoji
    virtual/freedesktop-icon-theme
"

pkg_setup() {
    export EGIT_COMMIT_DATE="$(echo ${PV} | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')"
    einfo "EGIT_COMMIT_DATE set to ${EGIT_COMMIT_DATE}"
}

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

    insinto "/etc/pam.d"
    newins "${FILESDIR}/pam-wbui" "wbui"

    insinto "/usr/lib/systemd/system"
    doins "${FILESDIR}/display-manager.service"
    doins "${FILESDIR}/wbui.service"
}

