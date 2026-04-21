EAPI=8

DESCRIPTION="Guest-side vsock-to-TCP bridge helper for VM sock-forward"

SLOT="0"
KEYWORDS="amd64 arm64"

RDEPEND="
	net-misc/socat
"

S="${WORKDIR}"

src_install() {
	exeinto /usr/bin
	doexe "${FILESDIR}/sock-forward"

	insinto /usr/lib/systemd/system
	newins "${FILESDIR}/sock-forward.service" "sock-forward@.service"
}
