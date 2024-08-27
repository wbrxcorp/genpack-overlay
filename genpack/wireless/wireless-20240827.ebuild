EAPI=8

DESCRIPTION="systemd-networkd config for wireless"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

S="${WORKDIR}"

RDEPEND="
	net-wireless/wpa_supplicant
	net-wireless/iw
	net-wireless/wireless-tools
	net-wireless/bluez
"

src_install() {
	insinto /etc/systemd/network
	doins "${FILESDIR}/54-wlan.network"
	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/wifi.py"
}

