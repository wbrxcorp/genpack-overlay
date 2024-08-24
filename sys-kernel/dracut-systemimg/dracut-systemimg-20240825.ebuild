EAPI=8

DESCRIPTION="stuffs for system.img"

SLOT="0"
KEYWORDS="amd64"

DEPEND="sys-kernel/dracut"

S="${WORKDIR}"

src_install() {
	exeinto /usr/lib/dracut/modules.d/90systemimg
	doexe "${FILESDIR}/check-systemimg-root.sh" "${FILESDIR}/module-setup.sh" "${FILESDIR}/mount-systemimg.sh"

	dodir /etc/dracut.conf.d
	echo 'early_microcode="no"' > "${D}/etc/dracut.conf.d/no-early_microcode.conf"
	echo 'omit_dracutmodules+=" systemd "' > "${D}/etc/dracut.conf.d/no-systemd.conf"
	echo 'add_dracutmodules+=" systemimg "' > "${D}/etc/dracut.conf.d/systemimg.conf"
}

