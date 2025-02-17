EAPI=8

inherit git-r3

DESCRIPTION="Create SR-IOV VFs"
HOMEPAGE="https://github.com/shimarin/create-sriov-vfs"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/create-sriov-vfs.git"
EGIT_COMMIT="d3659eaaa1e017eff73bc787d78b5598a64a0a8a"

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
