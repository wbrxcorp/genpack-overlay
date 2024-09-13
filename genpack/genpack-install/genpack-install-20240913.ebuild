EAPI=8
inherit git-r3

DESCRIPTION="system.img installer"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"
EGIT_COMMIT="c6839135ef655021fdd28636db8fc590fe11aec3"

SLOT="0"
KEYWORDS="amd64"

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

