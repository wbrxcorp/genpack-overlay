EAPI=8
inherit git-r3

DESCRIPTION="Paravirt virtual machine frontend"
HOMEPAGE="https://github.com/shimarin/vm"
EGIT_REPO_URI="https://github.com/shimarin/vm.git"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

DEPEND="
    dev-cpp/argparse dev-cpp/nlohmann_json
"

RDEPEND="
    app-emulation/qemu app-emulation/virtiofsd
    dev-libs/iniparser sys-apps/systemd sys-apps/util-linux sys-fs/squashfuse[lz4,lzma,lzo,zlib,zstd]
"

pkg_setup() {
    export EGIT_COMMIT_DATE="$(echo ${PV} | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')"
    einfo "EGIT_COMMIT_DATE set to ${EGIT_COMMIT_DATE}"
}

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

    # systemd service
    insinto /usr/lib/systemd/system
    newins "${FILESDIR}/vm.service" "vm@.service"

	# script for genpack
	exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
    doexe "${FILESDIR}/bridge-conf.sh"
}

