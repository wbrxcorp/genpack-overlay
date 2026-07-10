# Copyright 2026 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

inherit kernel-build

# Gateworks/linux-catalina branch v6.18.29-catalina (same revision as the
# factory-shipped kernel 6.18.29-g27aea7b19b24)
MY_COMMIT="27aea7b19b240e3b90e77cc4f685ed7078cb8387"
# Gateworks/bsp-catalina revision the defconfig is taken from
BSP_COMMIT="ce62c5825f9cfc0e3a04326297d2d1330bc9ec3c"

DESCRIPTION="Linux kernel for Gateworks Catalina (i.MX95) SBC"
HOMEPAGE="https://github.com/Gateworks/linux-catalina"
SRC_URI="
	https://github.com/Gateworks/linux-catalina/archive/${MY_COMMIT}.tar.gz
		-> linux-catalina-${PV}-${MY_COMMIT:0:8}.tar.gz
	https://raw.githubusercontent.com/Gateworks/bsp-catalina/${BSP_COMMIT}/configs/imx95_catalina_linux-6.18_defconfig
		-> imx95_catalina_linux-6.18_defconfig-${PV}-${BSP_COMMIT:0:8}
"
S="${WORKDIR}/linux-catalina-${MY_COMMIT}"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~arm64"
# kernel-build.eclass が src_install で無条件に `use debug` を参照するため宣言必須
# (eclass の IUSE は +strip modules-sign のみ。gentoo-kernel も ebuild 側で宣言している)
IUSE="debug"

src_prepare() {
	default

	# BSP defconfig をベースに使用
	cp "${DISTDIR}/imx95_catalina_linux-6.18_defconfig-${PV}-${BSP_COMMIT:0:8}" .config || die

	# genpack / dracut-genpack の動作に必要な追加設定
	cat > "${T}/genpack.config" <<-EOF
		# Magic SysRq (シリアルブレークでのハング復旧)
		CONFIG_MAGIC_SYSRQ=y
		# カーネルローカルバージョン
		CONFIG_LOCALVERSION="-catalina"
	EOF

	kernel-build_merge_configs "${T}/genpack.config"
}
