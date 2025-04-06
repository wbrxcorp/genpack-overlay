EAPI=8

DESCRIPTION="gnome environment"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

IUSE="+mozc"

RDEPEND="
    mozc? ( app-i18n/mozc )
    media-video/pipewire[gsettings,sound-server]
    gnome-base/gnome-shell[pipewire]
    net-misc/freerdp[server,openh264]
    x11-wm/mutter[screencast]
    gnome-base/gnome
    media-fonts/noto[cjk]
    media-fonts/noto-emoji
    x11-apps/mesa-progs
    dev-util/vulkan-tools
    net-libs/libnsl
    app-misc/evtest
    net-misc/gnome-remote-desktop
"

S="${WORKDIR}"

src_install() {
    dosym ../conf.avail/70-noto-cjk.conf /etc/fonts/conf.d/70-noto-cjk.conf
}
