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
	firmware? ( sys-kernel/linux-firmware )
	btrfs? ( sys-fs/btrfs-progs )
	xfs? ( sys-fs/xfsprogs )
"

S="${WORKDIR}"

src_install() {
	insinto /usr/lib/systemd/system
	doins "${FILESDIR}/systemimg-init.service" "${FILESDIR}/systemimg-shutdown.service"
	exeinto /usr/lib/systemimg
	doexe "${FILESDIR}/init" "${FILESDIR}/shutdown"
	insinto /usr/lib/systemimg/init.d
	doins "${FILESDIR}/autologin.py" "${FILESDIR}/hostname.py" "${FILESDIR}/install_memtest86.py" "${FILESDIR}/swapfile.py"
	insinto /usr/lib/systemimg/shutdown.d
	doins "${FILESDIR}/boottimetxt.py"
	insinto /usr/lib/genpack/systemimg
	doins "${FILESDIR}/grub.cfg"
	exeinto /usr/lib/genpack/package-scripts
	doexe "${FILESDIR}/systemimg.sh"
	doexe "${FILESDIR}/20-systemimg-installkernel.sh"
}

