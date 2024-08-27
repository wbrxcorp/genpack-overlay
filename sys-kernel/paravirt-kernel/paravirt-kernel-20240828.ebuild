EAPI=8

inherit genpack-ignore

DESCRIPTION="kernel and initramfs config for paravirt"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE="binary transient"

RDEPEND="
	!sys-kernel/systemimg-kernel
	binary? ( sys-kernel/gentoo-kernel-bin[initramfs] )
	!binary? ( sys-kernel/gentoo-kernel[initramfs] )
	sys-kernel/dracut
	app-admin/eclean-kernel
"

S="${WORKDIR}"

src_install() {
	exeinto /usr/lib/dracut/modules.d/90paravirt
	doexe "${FILESDIR}/module-setup.sh" "${FILESDIR}/mount-paravirt.sh" "${FILESDIR}/mount-paravirt-transient.sh"

	dodir /usr/lib/dracut/dracut.conf.d
	echo 'omit_dracutmodules+=" systemd "' > "${D}/usr/lib/dracut/dracut.conf.d/no-systemd.conf"
	echo 'add_dracutmodules+=" paravirt "' > "${D}/usr/lib/dracut/dracut.conf.d/paravirt.conf"
	if use transient; then
		echo 'genpack_transient=1' > "${D}/usr/lib/dracut/dracut.conf.d/genpack_transient.conf"
	fi

	dodir /usr/lib/genpack/package-scripts
	if use binary; then
		echo -e "#!/bin/sh\nemerge --config gentoo-kernel-bin" > "${D}/usr/lib/genpack/package-scripts/20-paravirt-installkernel.sh"
	else
		echo -e "#!/bin/sh\nemerge --config gentoo-kernel" > "${D}/usr/lib/genpack/package-scripts/20-paravirt-installkernel.sh"
	fi
	fperms 0755 /usr/lib/genpack/package-scripts/20-paravirt-installkernel.sh
}

