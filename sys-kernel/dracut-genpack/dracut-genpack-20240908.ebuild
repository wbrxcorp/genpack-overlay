EAPI=8

inherit genpack-ignore

DESCRIPTION="Dracut modules for genpack initramfs"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE="transient"

RDEPEND="
	sys-kernel/dracut
	sys-fs/dosfstools
"

S="${WORKDIR}"

src_install() {
	exeinto /usr/lib/dracut/modules.d/90genpack
	doexe "${FILESDIR}/check-systemimg-root.sh" "${FILESDIR}/module-setup.sh"
	cp "${FILESDIR}/mount-genpack.sh" "${T}/mount-genpack.sh"
	if use transient; then
		sed -i 's/^# transient=1$/transient=1/' "${T}/mount-genpack.sh"
	fi
	doexe "${T}/mount-genpack.sh"

	dodir /usr/lib/dracut/dracut.conf.d
	echo 'omit_dracutmodules+=" systemd "' > "${D}/usr/lib/dracut/dracut.conf.d/no-systemd.conf"
	echo 'add_dracutmodules+=" genpack "' > "${D}/usr/lib/dracut/dracut.conf.d/genpack.conf"
}

