EAPI=8

inherit git-r3

DESCRIPTION="Create SR-IOV VFs"
HOMEPAGE="https://github.com/shimarin/create-sriov-vfs"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/create-sriov-vfs.git"
EGIT_COMMIT="1363225d7a29418551a0794262d8ef874d46bfd9"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

BDEPEND="
    dev-cpp/argparse
"

src_install() {
	emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

	insinto /usr/lib/systemd/system
    doins "${S}/create-sriov-vfs-net@.service"
}
