EAPI=8
inherit genpack-ignore

DESCRIPTION="Support tools for genpack"
HOMEPAGE="https://github.com/wbrxcorp/genpack-progs"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

RDEPEND="
    sys-apps/util-linux app-portage/gentoolkit dev-util/pkgdev app-arch/zip dev-debug/strace
    net-analyzer/tcpdump app-editors/nano app-editors/vim net-misc/netkit-telnetd
    app-misc/figlet
    sys-fs/squashfs-tools[lz4,lzma,lzo,xattr,zstd]
    app-admin/eclean-kernel
"

src_unpack() {
    mkdir -p "${S}"
}

src_install() {
    exeinto "/usr/bin"
    newexe "${FILESDIR}/recursive-touch.py" recursive-touch
    newexe "${FILESDIR}/download.py" download
    newexe "${FILESDIR}/get-rpm-download-url.py" get-rpm-download-url
    newexe "${FILESDIR}/get-github-download-url.py" get-github-download-url
    newexe "${FILESDIR}/findelf.py" findelf
    newexe "${FILESDIR}/list-pkg-files.py" list-pkg-files
    newexe "${FILESDIR}/exec-package-scripts-and-generate-metadata.py" exec-package-scripts-and-generate-metadata
    newexe "${FILESDIR}/execute-artifact-build-scripts.py" execute-artifact-build-scripts
    newexe "${FILESDIR}/unmerge-masked-packages.sh" unmerge-masked-packages
    newexe "${FILESDIR}/rebuild-kernel-modules-if-necessary.sh" rebuild-kernel-modules-if-necessary
    newexe "${FILESDIR}/remove-binpkg.py" remove-binpkg
    newexe "${FILESDIR}/with-mysql.py" with-mysql
}
