EAPI=8
inherit git-r3

DESCRIPTION="Walbrix admin UI"
HOMEPAGE="https://github.com/wbrxcorp/wbui"
EGIT_REPO_URI="https://github.com/wbrxcorp/wbui.git"
EGIT_COMMIT="333942a173f8501c26d28a01cb9b6d2f9e8563da"

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

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

    insinto "/etc/pam.d"
    newins "${FILESDIR}/pam-wbui" "wbui"

    exeinto "/usr/lib/genpack-init"
    doexe "${FILESDIR}/installer.py"

    #insinto "/usr/lib/systemd/system"
    #doins "${FILESDIR}/display-manager.service"
    #doins "${FILESDIR}/wbui.service"
}

