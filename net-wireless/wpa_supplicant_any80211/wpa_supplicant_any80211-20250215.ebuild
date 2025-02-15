EAPI=8

inherit git-r3

DESCRIPTION="Just connect with any WiFi interface without specifying its exact name"
HOMEPAGE="https://github.com/shimarin/wpa_supplicant_any80211"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/wpa_supplicant_any80211.git"
EGIT_COMMIT="1cc100b28fa262159c628f678d17507a3e1d3e4f"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="
	net-wireless/wpa_supplicant
"
BDEPEND="
    dev-cpp/argparse
"

src_install() {
	emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

	insinto /usr/lib/systemd/system
    doins "${S}/wpa_supplicant_any80211.service"
}

