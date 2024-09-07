EAPI=8
inherit git-r3 genpack-ignore

DESCRIPTION="Support tools for genpack"
HOMEPAGE="https://github.com/wbrxcorp/genpack-progs"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-progs.git"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="
    sys-apps/util-linux app-portage/gentoolkit dev-util/pkgdev app-arch/zip dev-debug/strace
    net-analyzer/tcpdump app-editors/vim net-misc/netkit-telnetd
    app-misc/figlet
    app-admin/eclean-kernel
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
    # genpack-install is moved to separate package
    rm -f "${D}/usr/bin/genpack-install"

    exeinto "/usr/bin"
    newexe "${FILESDIR}/copyup-packages.py" copyup-packages
}

