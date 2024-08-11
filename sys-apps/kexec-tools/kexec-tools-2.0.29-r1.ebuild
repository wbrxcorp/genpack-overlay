EAPI=8

inherit libtool linux-info autotools

SRC_URI="https://www.kernel.org/pub/linux/utils/kernel/kexec/${P/_/-}.tar.xz"
KEYWORDS="riscv"

DESCRIPTION="Load another kernel from the currently executing Linux kernel"
HOMEPAGE="https://kernel.org/pub/linux/utils/kernel/kexec/"

S="${WORKDIR}/${P/_/-}"

LICENSE="GPL-2"
SLOT="0"
IUSE="lzma"

DEPEND="lzma? ( app-arch/xz-utils ) sys-libs/zlib"
RDEPEND="${DEPEND}"

CONFIG_CHECK="~KEXEC"

PATCHES=("${FILESDIR}"/riscv.patch)

pkg_setup() {
	export ASFLAGS="${CCASFLAGS}"
}

src_prepare() {
	default

	sed -e "/^PURGATORY_EXTRA_CFLAGS =/s/=/+=/" -i Makefile.in || die
	eautoreconf
}

src_configure() {
	econf "$(use_with lzma)" --with-zlib
}

src_compile() {
	local flag flags=()
	for flag in ${CFLAGS}; do
		[[ ${flag} == -mfunction-return=thunk ]] && flag="-mfunction-return=thunk-inline"
		[[ ${flag} == -mindirect-branch=thunk ]] && flag="-mindirect-branch=thunk-inline"
		flags+=("${flag}")
	done
	local -x PURGATORY_EXTRA_CFLAGS="${flags[*]}"

	default
}

src_install() {
	default
}

