EAPI=8

DESCRIPTION="Metapackage for wireless"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

S="${WORKDIR}"

RDEPEND="
	net-wireless/wpa_supplicant_any80211
	net-wireless/iw
	net-wireless/wireless-tools
	net-wireless/bluez
	net-wireless/hostapd
"
