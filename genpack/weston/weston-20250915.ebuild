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

S="${WORKDIR}"

src_install() {
    insinto /etc/skel/.config/fcitx5
    newins "${FILESDIR}"/fcitx5-config config
    newins "${FILESDIR}"/fcitx5-profile profile

    exeinto /usr/lib/genpack/package-scripts/app-i18n/fcitx
    doexe "${FILESDIR}"/add-fcitx-to-weston-ini.sh

    exeinto /usr/lib/genpack/package-scripts/media-fonts/noto-cjk
    doexe "${FILESDIR}"/enable-noto-cjk.sh

    if use greeter ; then
        exeinto /usr/lib/genpack/package-scripts/gui-libs/greetd
        doexe "${FILESDIR}"/setup-greetd.sh
    fi
}
