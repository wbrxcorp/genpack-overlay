EAPI=8

DESCRIPTION="gnome environment"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+mozc"

RDEPEND="
    mozc? ( app-i18n/mozc )
    gnome-base/gnome
    media-fonts/noto-cjk
    media-fonts/noto-emoji
    x11-apps/mesa-progs
    dev-util/vulkan-tools
    net-libs/libnsl
    app-misc/evtest
    net-misc/gnome-remote-desktop
"

S="${WORKDIR}"

src_install() {
    exeinto /usr/lib/genpack/package-scripts/media-fonts/noto-cjk
    doexe "${FILESDIR}"/enable-noto-cjk.sh
}
