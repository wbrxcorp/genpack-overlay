EAPI=8
inherit git-r3

DESCRIPTION="Walbrix admin command"
HOMEPAGE="https://github.com/wbrxcorp/wb"
EGIT_REPO_URI="https://github.com/wbrxcorp/wb.git"
EGIT_COMMIT="0cdfb4a"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

DEPEND="
    dev-cpp/argparse dev-cpp/nlohmann_json net-libs/wghub
"

RDEPEND="
    >=dev-libs/iniparser-4.2.5 sys-apps/util-linux sys-fs/btrfs-progs 
    net-misc/curl dev-libs/openssl media-gfx/qrencode dev-libs/wayland
    net-vpn/wireguard-tools
    app-emulation/vm
"

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

    # systemd service
    insinto /usr/lib/systemd/system
    doins "${FILESDIR}/scan-volumes.service"
    doins "${FILESDIR}/notify-status.service"

    # script for genpack-init
    exeinto /usr/lib/genpack-init
    doexe "${FILESDIR}/default_volume.py"
    doexe "${FILESDIR}/generate_privkey.py"
    doexe "${FILESDIR}/wg-walbrix.py"

	# script for genpack
	exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
    doexe "${FILESDIR}/enable-services.sh"
}

