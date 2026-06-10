EAPI=8

PYTHON_COMPAT=( python3_{13..15} )

inherit git-r3
inherit python-single-r1

DESCRIPTION="Intermediate init for genpack system"
HOMEPAGE="https://github.com/wbrxcorp/genpack-init"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-init.git"
EGIT_COMMIT="e0cc980b81509f98605ab08291f7f13324a60a6c"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE="exec-guard"

RDEPEND="${PYTHON_DEPS}
	exec-guard? ( dev-libs/libbpf )"
DEPEND="${RDEPEND}"
BDEPEND="$(python_gen_cond_dep 'dev-python/pybind11[${PYTHON_USEDEP}]') dev-cpp/argparse
	exec-guard? ( dev-util/bpftool llvm-core/clang )"

src_compile() {
	emake $(usex exec-guard "WITH_EXEC_GUARD=1" "") PYTHON=${EPYTHON} genpack-init || die "emake failed"
}

src_install() {
	emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"

	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/99default_network_interface.py"

	dodir /usr/lib/dracut/dracut.conf.d
	echo 'realinitpath="/usr/bin/genpack-init"' > "${D}/usr/lib/dracut/dracut.conf.d/realinitpath.conf"

	if use exec-guard; then
		insinto /etc/audit/rules.d
		doins "${FILESDIR}/exec_guard.rules"
	fi
}
