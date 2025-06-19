EAPI=8

DESCRIPTION="Systemd service to bridge arbitrary ports to AF_VSOCK sockets"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

RDEPEND="
	net-misc/socat
"

S="${WORKDIR}"

src_install() {
    insinto /usr/lib/systemd/system
    newins "${FILESDIR}/socat-vsock.service" "socat-vsock@.service"
}
