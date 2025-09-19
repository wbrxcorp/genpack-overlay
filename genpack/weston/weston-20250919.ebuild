EAPI=8

DESCRIPTION="Weston environment"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+greeter"

RDEPEND="
    dev-libs/weston
    app-i18n/mozc
    app-i18n/fcitx-gtk
    greeter? ( gui-apps/tuigreet )
    media-fonts/noto-cjk
    media-fonts/noto-emoji
    x11-apps/mesa-progs
    dev-util/vulkan-tools
"
PDEPEND="
    media-libs/vips
    gnome-base/librsvg
"
S="${WORKDIR}"

src_install() {
    insinto /etc/skel/.config
    doins "${FILESDIR}"/weston.ini

    insinto /etc/skel/.config/fcitx5
    newins "${FILESDIR}"/fcitx5-config config
    newins "${FILESDIR}"/fcitx5-profile profile

    exeinto /usr/lib/genpack/package-scripts/media-fonts/noto-cjk
    doexe "${FILESDIR}"/enable-noto-cjk.sh

    if use greeter ; then
        exeinto /usr/lib/genpack/package-scripts/gui-libs/greetd
        doexe "${FILESDIR}"/setup-greetd.sh
    fi

    exeinto /usr/lib/genpack/package-scripts/app-i18n/fcitx
    doexe "${FILESDIR}"/weston-ini/fcitx.sh

    exeinto /usr/lib/genpack/package-scripts/www-client/google-chrome
    doexe "${FILESDIR}"/weston-ini/chrome.sh

    exeinto /usr/lib/genpack/package-scripts/app-editors/vscode
    doexe "${FILESDIR}"/weston-ini/vscode.sh

    exeinto /usr/lib/genpack/package-scripts/x11-terms/ghostty
    doexe "${FILESDIR}"/weston-ini/ghostty.sh

    exeinto /usr/lib/genpack/package-scripts/app-editors/gnome-text-editor
    doexe "${FILESDIR}"/weston-ini/gnome-text-editor.sh

    exeinto /usr/lib/genpack/package-scripts/media-gfx/gimp
    doexe "${FILESDIR}"/weston-ini/gimp.sh

    exeinto /usr/lib/genpack/package-scripts/mail-client/evolution
    doexe "${FILESDIR}"/weston-ini/evolution.sh

    exeinto /usr/lib/genpack/package-scripts/app-office/libreoffice
    doexe "${FILESDIR}"/weston-ini/libreoffice.sh

    exeinto /usr/lib/genpack/package-scripts/gnome-base/nautilus
    doexe "${FILESDIR}"/weston-ini/nautilus.sh

    exeinto /usr/lib/genpack/package-scripts/media-video/vlc
    doexe "${FILESDIR}"/weston-ini/vlc.sh

    exeinto /usr/lib/genpack/package-scripts/media-sound/rhythmbox
    doexe "${FILESDIR}"/weston-ini/rhythmbox.sh

    exeinto /usr/lib/genpack/package-scripts/net-misc/remmina
    doexe "${FILESDIR}"/weston-ini/remmina.sh
}
