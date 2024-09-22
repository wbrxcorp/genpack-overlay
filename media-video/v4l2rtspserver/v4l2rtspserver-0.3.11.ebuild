EAPI=8

inherit unpacker

DESCRIPTION="RTSP Server for V4L2 device capture"
HOMEPAGE="https://github.com/mpromonet/v4l2rtspserver"

ARCH_DEB=""
case ${ARCH} in
    amd64)
        ARCH_DEB="x86_64"
        ;;
    arm64)
        ARCH_DEB="arm64"
        ;;
    riscv)
        ARCH_DEB="riscv64"
        ;;
    *)
        die "Unsupported architecture: ${ARCH}"
        ;;
esac

SRC_URI="https://github.com/mpromonet/v4l2rtspserver/releases/download/v${PV}/${P}-Linux-${ARCH_DEB}-Release.deb"
S="${WORKDIR}"

LICENSE="Unlicense"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

DEPEND="app-arch/dpkg"
RDEPEND="dev-libs/openssl-compat"

QA_PREBUILT="*"

src_install() {
    exeinto "/usr/bin"
    doexe "${WORKDIR}/usr/local/bin/v4l2rtspserver" || die "Failed to install binary"
    insinto "/usr/share"
    doins -r "${WORKDIR}/usr/local/share/v4l2rtspserver" || die "Failed to install files"
    sed -i 's/^ExecStart=\(.*\)$/ExecStart=\1 -P 554 -u "" -f -F 0/' "${WORKDIR}/lib/systemd/system/v4l2rtspserver.service" || die "Failed to modify service file"
    sed -i 's/\/usr\/local\//\/usr\//g' "${WORKDIR}/lib/systemd/system/v4l2rtspserver.service" || die "Failed to modify service file"
    insinto "/usr/lib/systemd/system"
    doins "${WORKDIR}/lib/systemd/system/v4l2rtspserver.service" || die "Failed to install service file"
}