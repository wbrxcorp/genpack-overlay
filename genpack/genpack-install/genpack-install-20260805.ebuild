EAPI=8
inherit git-r3

DESCRIPTION="system.img installer and ISO/ZIP image builders"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"
EGIT_COMMIT="f1e6f73b39c63ddf6c980a737ce301f059877035"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

# genpack-mkiso and genpack-mkzip only ever run on a build host, so an artifact
# can leave them out and avoid carrying libisofs or minizip. With all three off,
# only the bootloader files under /usr/lib/genpack-install are installed, which
# is what genpack-mkiso reads out of a system image.
IUSE="+install iso zip test"
RESTRICT="!test? ( test )"

# grub, dosfstools and mtools build the bootloader files, which happens
# whichever tools are selected.
DEPEND="
	dev-cpp/argparse
	virtual/pkgconfig
	sys-boot/grub
	sys-fs/dosfstools
	sys-fs/mtools
	sys-fs/squashfs-tools-ng
	install? ( sys-apps/util-linux )
	iso? ( dev-libs/libisofs )
	zip? ( sys-libs/zlib[minizip] )
	test? ( dev-cpp/doctest )
"
RDEPEND="
	install? (
		sys-apps/util-linux
		sys-block/parted
		sys-fs/dosfstools
		sys-fs/btrfs-progs
		sys-fs/squashfs-tools-ng
		app-arch/unzip
		sys-boot/grub
	)
	iso? ( dev-libs/libisofs sys-fs/squashfs-tools-ng )
	zip? ( sys-libs/zlib[minizip] sys-fs/squashfs-tools-ng )
"

selected_tools() { echo "$(usev install) $(usev iso) $(usev zip)"; }

src_compile() {
    emake TOOLS="$(selected_tools)" || die "emake failed"
}

src_test() {
    emake TOOLS="$(selected_tools)" test || die "emake test failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" TOOLS="$(selected_tools)" install || die "emake install failed"

	# install grub-bios-setup
	if use install; then
		exeinto /usr/lib/genpack/package-scripts/genpack/genpack-install
		doexe "${FILESDIR}/copyup-grub-bios-setup.sh"
	fi
}
