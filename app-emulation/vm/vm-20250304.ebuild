EAPI=8
inherit git-r3

DESCRIPTION="Paravirt virtual machine frontend"
HOMEPAGE="https://github.com/shimarin/vm"
EGIT_REPO_URI="https://github.com/shimarin/vm.git"
EGIT_COMMIT="d0e9cd6d58eadf881685637ac677ae0180bb4d83"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

DEPEND="
    dev-cpp/argparse dev-cpp/nlohmann_json
"

RDEPEND="
    app-emulation/qemu app-emulation/virtiofsd
    >=dev-libs/iniparser-4.2.5 sys-apps/systemd sys-apps/util-linux 
    sys-fs/squashfuse[lz4,lzma,lzo,zlib,zstd]
    dev-cpp/libxmlpp
"
src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

    # systemd service
    insinto /usr/lib/systemd/system
    newins "${FILESDIR}/vm.service" "vm@.service"
    newins "${FILESDIR}/mirrortap.service" "mirrortap@.service"

	# script for genpack
	exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
    doexe "${FILESDIR}/bridge-conf.sh"
}

