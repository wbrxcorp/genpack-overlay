EAPI=8
inherit git-r3

DESCRIPTION="system.img installer"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"
EGIT_COMMIT="c456b5b2e934ed7a281dc3c05d9840f95500f0c3"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

DEPEND="dev-cpp/argparse sys-fs/mtools sys-boot/grub"
RDEPEND="
	sys-libs/zlib[minizip]
	sys-block/parted
	sys-fs/dosfstools
	dev-libs/libisoburn
	sys-fs/btrfs-progs
	app-arch/unzip
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

	# install grub-bios-setup
	exeinto /usr/lib/genpack/package-scripts/genpack/genpack-install
	doexe "${FILESDIR}/copyup-grub-bios-setup.sh"
}

