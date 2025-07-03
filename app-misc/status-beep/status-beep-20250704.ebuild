EAPI=8

inherit systemd

DESCRIPTION="Systemd service to beep at system startup/shutdown"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

RDEPEND="app-misc/beep net-misc/openssh"

S="${WORKDIR}"

src_install() {
    systemd_dounit "${FILESDIR}/status-beep.service"
}
