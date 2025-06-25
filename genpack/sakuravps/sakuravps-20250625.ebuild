EAPI=8

DESCRIPTION="Basic dependencies for sakuravps"

SLOT="0"
KEYWORDS="amd64"

RDEPEND="
    genpack/systemimg[-baremetal]
    app-emulation/qemu-guest-agent
    sys-process/iotop
    app-admin/sysstat
    app-misc/screen
    dev-libs/openssl-compat
    net-analyzer/tcpdump
    net-analyzer/snort
    net-analyzer/traceroute
    net-dns/bind-tools
    net-misc/bridge-utils
    net-misc/iperf
    sys-fs/xfsprogs
    sys-process/lsof
    net-misc/whois
    net-ftp/ftp
    net-analyzer/zabbix
    net-vpn/wireguard-tools
    net-firewall/ipset
    net-firewall/firewalld
    net-firewall/xtables-addons
    net-misc/socat
"

S="${WORKDIR}"

src_install() {
    # Install the init script for MySQL
    insinto /usr/lib/genpack-init
    doins ${FILESDIR}/50sakuravps.py
}