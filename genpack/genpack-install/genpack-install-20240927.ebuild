EAPI=8
inherit git-r3

DESCRIPTION="system.img installer"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"
EGIT_COMMIT="7e2a398af57d50f5d92ec3a772acc186a33c64a3"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

DEPEND="dev-cpp/argparse"
RDEPEND="
	sys-block/parted
	sys-fs/dosfstools
	sys-boot/grub
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

