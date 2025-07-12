EAPI=8

PYTHON_COMPAT=( python3_13 )
DISTUTILS_USE_PEP517=setuptools
inherit distutils-r1 pypi systemd

DESCRIPTION="Python package to generate country-specific IP network ranges consumable by both iptables/ipset and nftables"
HOMEPAGE="https://github.com/chr0mag/geoipsets"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

RDEPEND="
    net-firewall/nftables
    dev-python/beautifulsoup4
    dev-python/requests"

python_install_all() {
    distutils-r1_python_install_all
    systemd_dounit "${FILESDIR}/update-geoipsets.service"
    systemd_dounit "${FILESDIR}/update-geoipsets.timer"
}
