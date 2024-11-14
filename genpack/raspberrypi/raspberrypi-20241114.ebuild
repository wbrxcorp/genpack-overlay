EAPI=8

DESCRIPTION="Metapackage for raspberry pi"

SLOT="0"
KEYWORDS="arm64"

RDEPEND="
	genpack/systemimg
	sys-kernel/raspberrypi-image
	media-libs/raspberrypi-userland-bin
	sys-firmware/raspberrypi-wireless-firmware
"

S="${WORKDIR}"

