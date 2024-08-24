EAPI=8

DESCRIPTION="systemd-networkd config for bridged ethernet"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

S="${WORKDIR}"

src_install() {
	insinto /etc/systemd/network
	doins "${FILESDIR}/48-br0.netdev" "${FILESDIR}/50-eth.network" "${FILESDIR}/52-br0.network"
}

