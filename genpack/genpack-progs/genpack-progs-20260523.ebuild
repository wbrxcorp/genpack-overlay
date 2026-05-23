EAPI=8

PYTHON_COMPAT=( python3_{12..13} )
inherit python-single-r1 genpack-ignore

DESCRIPTION="Support tools for genpack"
HOMEPAGE="https://github.com/wbrxcorp/genpack-progs"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

REQUIRED_USE="${PYTHON_REQUIRED_USE}"

RDEPEND="
    ${PYTHON_DEPS}
    sys-apps/util-linux app-portage/gentoolkit dev-util/pkgdev app-arch/zip dev-debug/strace
    net-analyzer/tcpdump app-editors/nano app-editors/vim net-misc/netkit-telnetd
    app-misc/figlet
    sys-fs/squashfs-tools[lz4,lzma,lzo,xattr,zstd]
    sys-fs/mtools
    app-admin/eclean-kernel
    dev-python/tqdm
"

src_unpack() {
    mkdir -p "${S}"
}

src_install() {
    python_domodule "${FILESDIR}/genpack_pkg.py"

    exeinto "/usr/bin"
    newexe "${FILESDIR}/recursive-touch.py" recursive-touch
    newexe "${FILESDIR}/download.py" download
    newexe "${FILESDIR}/get-rpm-download-url.py" get-rpm-download-url
    newexe "${FILESDIR}/get-github-download-url.py" get-github-download-url
    newexe "${FILESDIR}/findelf.py" findelf
    # kept for backward compatibility with older genpack versions
    newexe "${FILESDIR}/list-pkg-files.py" list-pkg-files
    newexe "${FILESDIR}/exec-package-scripts-and-generate-metadata.py" exec-package-scripts-and-generate-metadata
    newexe "${FILESDIR}/genpack-exec-package-scripts.py" genpack-exec-package-scripts
    newexe "${FILESDIR}/genpack-copyup.py" genpack-copyup
    newexe "${FILESDIR}/execute-artifact-build-scripts.py" execute-artifact-build-scripts
    newexe "${FILESDIR}/unmerge-masked-packages.sh" unmerge-masked-packages
    newexe "${FILESDIR}/genpack-unmerge-masked-packages.sh" genpack-unmerge-masked-packages
    newexe "${FILESDIR}/rebuild-kernel-modules-if-necessary.sh" rebuild-kernel-modules-if-necessary
    newexe "${FILESDIR}/remove-binpkg.py" remove-binpkg
    newexe "${FILESDIR}/with-mysql.py" with-mysql
    newexe "${FILESDIR}/require-installed.py" require-installed
    newexe "${FILESDIR}/genpack-create-image.py" genpack-create-image
}
