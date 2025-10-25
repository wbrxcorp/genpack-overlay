EAPI=8

DESCRIPTION="stuffs for system.img"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE="baremetal"

RDEPEND="
	genpack/base
	!genpack/paravirt
	genpack/genpack-install
	sys-apps/kbd
	baremetal? ( 
		|| ( sys-kernel/linux-firmware sys-firmware/raspberrypi-wifi-ucode )
		sys-fs/lsscsi
		sys-apps/lshw
		sys-apps/hwloc
		sys-apps/usbutils
		sys-apps/pciutils
		sys-apps/dmidecode
		sys-apps/lm-sensors
		sys-apps/usb_modeswitch
		sys-power/cpupower
		sys-apps/smartmontools
		sys-apps/hdparm
		sys-apps/ethtool
		amd64? ( 
			app-misc/beep
			sys-apps/msr-tools 
			sys-apps/memtest86+
		)
	)
"

S="${WORKDIR}"

src_install() {
	# configuration scripts called by systemimg-init
	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/autologin.py" "${FILESDIR}/hostname.py" "${FILESDIR}/install_memtest86.py" "${FILESDIR}/swapfile.py"

	# enable getty@tty1
	exeinto /usr/lib/genpack/package-scripts/sys-apps/systemd
	doexe "${FILESDIR}/enable-getty-at-tty1.sh"

	exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
	doexe "${FILESDIR}/systemimg.sh"

	exeinto /usr/lib/genpack/package-scripts/sys-kernel/raspberrypi-image
	doexe "${FILESDIR}/raspberrypi-generate-initramfs.py"
}
