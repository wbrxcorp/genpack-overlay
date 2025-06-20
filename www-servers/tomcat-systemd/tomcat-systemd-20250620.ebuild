EAPI=8

DESCRIPTION="Systemd service to manage Tomcat"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

RDEPEND="
	www-servers/tomcat
"

S="${WORKDIR}"

src_install() {
    exeinto /usr/bin
    doexe "${FILESDIR}/tomcat"

    insinto /usr/lib/systemd/system
    doins "${FILESDIR}/tomcat.service"

    insinto /etc/tmpfiles.d
    doins "${FILESDIR}/tomcat.conf"
}
