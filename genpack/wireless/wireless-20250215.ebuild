EAPI=8

DESCRIPTION="systemd-networkd config for wireless"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

S="${WORKDIR}"

RDEPEND="
	net-wireless/wpa_supplicant_any80211
	net-wireless/iw
	net-wireless/wireless-tools
	net-wireless/bluez
	net-wireless/hostapd
"

src_install() {
	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/wifi.py"
}

