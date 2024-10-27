EAPI=8

DESCRIPTION="Ready-to-use SRT / WebRTC / RTSP / RTMP / LL-HLS media server"
HOMEPAGE="https://github.com/bluenviron/mediamtx"

BASE_URI="https://github.com/bluenviron/mediamtx/releases/download/v${PV}/${PN}_v${PV}_linux_"
SRC_URI="
        amd64? ( ${BASE_URI}amd64.tar.gz )
        arm64? ( ${BASE_URI}arm64v8.tar.gz )
"

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
