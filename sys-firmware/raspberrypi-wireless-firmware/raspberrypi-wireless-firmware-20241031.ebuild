EAPI=8

inherit unpacker

DESCRIPTION="Proprietary wireless firmware for Raspberry Pi"
HOMEPAGE="https://github.com/RPi-Distro"

SRC_URI="http://archive.raspberrypi.com/debian/pool/main/b/bluez-firmware/bluez-firmware_1.2-9+rpt3_all.deb http://archive.raspberrypi.com/debian/pool/main/f/firmware-nonfree/firmware-brcm80211_20230625-2+rpt3_all.deb"
S="${WORKDIR}"

LICENSE="Broadcom"
SLOT="0"
KEYWORDS="arm64"
IUSE=""

RDEPEND="
	net-wireless/wireless-regdb
	!sys-firmware/raspberrypi-wifi-ucode
	!sys-kernel/linux-firmware[-savedconfig]
"

QA_PREBUILT="*"

src_configure() {
	ln -rs "${WORKDIR}"/lib/firmware/cypress/cyfmac43455-sdio-standard.bin "${WORKDIR}"/lib/firmware/cypress/cyfmac43455-sdio.bin
}

src_install() {
	insinto "/usr/lib"
	doins -r "${WORKDIR}/lib/firmware"
}

