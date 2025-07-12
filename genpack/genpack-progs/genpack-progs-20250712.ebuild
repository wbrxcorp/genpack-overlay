EAPI=8
inherit git-r3 genpack-ignore

DESCRIPTION="Support tools for genpack"
HOMEPAGE="https://github.com/wbrxcorp/genpack-progs"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-progs.git"
EGIT_COMMIT="be3179c"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

RDEPEND="
    sys-apps/util-linux app-portage/gentoolkit dev-util/pkgdev app-arch/zip dev-debug/strace
    net-analyzer/tcpdump app-editors/nano app-editors/vim net-misc/netkit-telnetd
    app-misc/figlet
    app-admin/eclean-kernel
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" install || die "emake install failed"
    # genpack-install is moved to separate package
    rm -f "${D}/usr/bin/genpack-install" "${D}/usr/bin/install-cloudflared"
    # with-mysql is moved to this ebuild
    rm -f "${D}/usr/local/sbin/with-mysql"

    exeinto "/usr/bin"
    newexe "${FILESDIR}/copyup-packages.py" copyup-packages # will be deprecated
    newexe "${FILESDIR}/genpack-prepare.py" genpack-prepare # will be deprecated
    newexe "${FILESDIR}/list-pkg-files.py" list-pkg-files
    newexe "${FILESDIR}/exec-package-scripts-and-generate-metadata.py" exec-package-scripts-and-generate-metadata
    newexe "${FILESDIR}/unmerge-masked-packages.sh" unmerge-masked-packages
    newexe "${FILESDIR}/check-unwanted-pythons.py" check-unwanted-pythons # will be deprecated
    newexe "${FILESDIR}/with-mysql.py" with-mysql
}
