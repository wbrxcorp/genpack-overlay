EAPI=8
inherit git-r3

DESCRIPTION="system.img installer"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"
EGIT_COMMIT="0859012efb5ae7ca1a76ba744b8981593689145f"

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
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" install || die "emake install failed"
}

