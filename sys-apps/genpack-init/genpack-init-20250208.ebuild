EAPI=8

PYTHON_COMPAT=( python3_12 )

inherit git-r3
inherit python-single-r1

DESCRIPTION="Intermediate init for genpack system"
HOMEPAGE="https://github.com/wbrxcorp/genpack-init"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-init.git"
EGIT_COMMIT="563f8802da3ccd5348ebae9c92b4cad44282d80e"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="${PYTHON_DEPS}"
DEPEND="${RDEPEND}"
BDEPEND="$(python_gen_cond_dep 'dev-python/pybind11[${PYTHON_USEDEP}]') dev-cpp/argparse"

src_compile() {
	emake PYTHON=${EPYTHON} genpack-init || die "emake failed"
}

src_install() {
	emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/99default_network_interface.py"

	dodir /usr/lib/dracut/dracut.conf.d
	echo 'realinitpath="/usr/bin/genpack-init"' > "${D}/usr/lib/dracut/dracut.conf.d/realinitpath.conf"
}

