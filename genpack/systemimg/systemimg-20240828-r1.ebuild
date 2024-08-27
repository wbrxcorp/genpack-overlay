EAPI=8

DESCRIPTION="stuffs for system.img"

SLOT="0"
KEYWORDS="amd64"
IUSE="baremetal +btrfs +xfs"

RDEPEND="
	!genpack/paravirt
	sys-kernel/genpack-kernel
	sys-apps/genpack-init
	genpack/genpack-install
	baremetal? ( 
		sys-kernel/linux-firmware
		sys-fs/lsscsi
		sys-apps/lshw
		sys-apps/hwloc
		sys-apps/msr-tools
		sys-apps/usbutils
		sys-apps/pciutils
		sys-apps/dmidecode
		sys-apps/lm-sensors
		sys-apps/usb_modeswitch
		sys-power/cpupower
		sys-apps/smartmontools
		sys-apps/ethtool
		app-misc/beep
		sys-apps/memtest86+
	)
	btrfs? ( sys-fs/btrfs-progs )
	xfs? ( sys-fs/xfsprogs )
"

S="${WORKDIR}"

src_install() {
	# configuration scripts called by systemimg-init
	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/autologin.py" "${FILESDIR}/hostname.py" "${FILESDIR}/install_memtest86.py" "${FILESDIR}/swapfile.py"

	# shutdown script
	insinto /usr/lib/systemd/system
	doins "${FILESDIR}/cleanup-boottimetxt.service"

	# script for genpack
	insinto /usr/lib/genpack/systemimg
	doins "${FILESDIR}/grub.cfg"
	exeinto /usr/lib/genpack/package-scripts
	doexe "${FILESDIR}/systemimg.sh"
}