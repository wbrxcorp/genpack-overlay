EAPI=8

DESCRIPTION="stuffs for system.img"

SLOT="0"
KEYWORDS="amd64"
IUSE="+firmware +btrfs +xfs"

DEPEND="
	sys-kernel/gentoo-kernel[initramfs]
	app-admin/eclean-kernel
	sys-kernel/dracut-systemimg
"

RDEPEND="
	genpack/genpack-install
	firmware? ( sys-kernel/linux-firmware[-initramfs] )
	btrfs? ( sys-fs/btrfs-progs )
	xfs? ( sys-fs/xfsprogs )
"

S="${WORKDIR}"

src_install() {
	insinto /usr/lib/systemd/system
	doins "${FILESDIR}/systemimg-init.service" "${FILESDIR}/systemimg-shutdown.service"
	exeinto /usr/lib/systemimg
	doexe "${FILESDIR}/init"
	insinto /usr/lib/systemimg/init.d
	doins "${FILESDIR}/autologin.py" "${FILESDIR}/hostname.py" "${FILESDIR}/install_memtest86.py" "${FILESDIR}/swapfile.py"
	insinto /boot/grub
	doins "${FILESDIR}/grub.cfg"
}

