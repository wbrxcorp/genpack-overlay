EAPI=8

inherit git-r3

DESCRIPTION="Create SR-IOV VFs"
HOMEPAGE="https://github.com/shimarin/create-sriov-vfs"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/create-sriov-vfs.git"
EGIT_COMMIT="138c64d15403f34612f2e0832fd6fdf791a9c6c6"

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
