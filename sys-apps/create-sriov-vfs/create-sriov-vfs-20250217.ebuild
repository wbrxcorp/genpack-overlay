EAPI=8

inherit git-r3

DESCRIPTION="Create SR-IOV VFs"
HOMEPAGE="https://github.com/shimarin/create-sriov-vfs"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/create-sriov-vfs.git"
EGIT_COMMIT="f2bab8eef75e3c93a4ebb87705acec3f635a8c8c"

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
