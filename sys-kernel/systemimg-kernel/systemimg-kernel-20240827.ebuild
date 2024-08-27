EAPI=8

DESCRIPTION="kernel and initramfs config for system.img"

SLOT="0"
KEYWORDS="amd64"
IUSE="+genpack-ignore +binary"

RDEPEND="
	!sys-kernel/paravirt-kernel
	binary? ( sys-kernel/gentoo-kernel-bin[initramfs] )
	!binary? ( sys-kernel/gentoo-kernel[initramfs] )
	sys-kernel/dracut
	app-admin/eclean-kernel
"

S="${WORKDIR}"

src_install() {
	exeinto /usr/lib/dracut/modules.d/90systemimg
	doexe "${FILESDIR}/check-systemimg-root.sh" "${FILESDIR}/module-setup.sh" "${FILESDIR}/mount-systemimg.sh"

	dodir /usr/lib/dracut/dracut.conf.d
	echo 'omit_dracutmodules+=" systemd "' > "${D}/usr/lib/dracut/dracut.conf.d/no-systemd.conf"
	echo 'add_dracutmodules+=" systemimg "' > "${D}/usr/lib/dracut/dracut.conf.d/systemimg.conf"
	echo 'realinitpath="/usr/bin/systemimg-init"' > "${D}/usr/lib/dracut/dracut.conf.d/realinitpath.conf"

	dodir /usr/lib/genpack/package-scripts
	if use binary; then
		echo -e "#!/bin/sh\nemerge --config gentoo-kernel-bin" > "${D}/usr/lib/genpack/package-scripts/20-systemimg-installkernel.sh"
	else
		echo -e "#!/bin/sh\nemerge --config gentoo-kernel" > "${D}/usr/lib/genpack/package-scripts/20-systemimg-installkernel.sh"
	fi
	fperms 0755 /usr/lib/genpack/package-scripts/20-systemimg-installkernel.sh
}

