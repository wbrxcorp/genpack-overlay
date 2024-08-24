EAPI=8
inherit git-r3

DESCRIPTION="system.img installer"
HOMEPAGE="https://github.com/wbrxcorp/genpack-install"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-install.git"

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

pkg_setup() {
    export EGIT_COMMIT_DATE="$(echo ${PV} | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')"
    einfo "EGIT_COMMIT_DATE set to ${EGIT_COMMIT_DATE}"
}

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" install || die "emake install failed"
}

