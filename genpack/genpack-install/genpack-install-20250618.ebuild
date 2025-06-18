EAPI=8
inherit git-r3

DESCRIPTION="system.img installer"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"
EGIT_COMMIT="96300b170021fe5152793fee181169c856ea8375"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

DEPEND="dev-cpp/argparse"
RDEPEND="
	sys-libs/zlib[minizip]
	sys-block/parted
	sys-fs/dosfstools
	sys-boot/grub
	sys-boot/genpack-bootloader
	sys-fs/mtools
	dev-libs/libisoburn
	sys-apps/kbd
	sys-fs/btrfs-progs
	app-arch/unzip
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}

