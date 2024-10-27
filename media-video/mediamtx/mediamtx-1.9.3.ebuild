EAPI=8

DESCRIPTION="Ready-to-use SRT / WebRTC / RTSP / RTMP / LL-HLS media server"
HOMEPAGE="https://github.com/bluenviron/mediamtx"

ARCH_DIST=""
case ${ARCH} in
    amd64)
        ARCH_DIST="amd64"
        ;;
    arm64)
        ARCH_DIST="arm64v8"
        ;;
    *)
        die "Unsupported architecture: ${ARCH}"
        ;;
esac

SRC_URI="https://github.com/bluenviron/mediamtx/releases/download/v${PV}/${PN}_v${PV}_linux_${ARCH_DIST}.tar.gz"
S="${WORKDIR}"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64"
IUSE=""

QA_PREBUILT="*"

src_install() {
    exeinto "/usr/bin"
    doexe "${WORKDIR}/mediamtx" || die "Failed to install binary"
    insinto "/etc/mediamtx"
    doins "${WORKDIR}/mediamtx.yml" || die "Failed to install default config file"
    insinto "/usr/lib/systemd/system"
    doins "${FILESDIR}/mediamtx.service" || die "Failed to install service file"
}