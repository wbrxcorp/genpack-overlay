EAPI=8

inherit genpack-ignore

DESCRIPTION="kernel and initramfs config for genpack images"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE="+binary transient"

RDEPEND="
	binary? ( sys-kernel/gentoo-kernel-bin[initramfs] )
	!binary? ( sys-kernel/gentoo-kernel[initramfs] )
	sys-kernel/dracut
	app-admin/eclean-kernel
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

