# Copyright 2026 Walbrix Corporation
# Distributed under the terms of the MIT License

EAPI=8

DESCRIPTION="U-Boot extlinux boot files for Gateworks Catalina (i.MX95) SBC"
HOMEPAGE="https://github.com/wbrxcorp/genpack-overlay"
S="${WORKDIR}"

LICENSE="MIT"
SLOT="0"
KEYWORDS="~arm64"

RDEPEND="sys-kernel/catalina-kernel"

src_install() {
    # genpack-install はイメージ内の boot/extlinux/extlinux.conf を
    # 「U-Boot extlinux SBC」のマーカーとして検出し、conf が参照する
    # ファイルだけをブートパーティションへコピーする
    insinto /boot/extlinux
    doins "${FILESDIR}/extlinux.conf"

    # イメージビルド時に DTB を /boot へ複製する package-script
    exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
    doexe "${FILESDIR}/copy-dtb.sh"

    # catalina-kernel は virtual/dist-kernel のプロバイダではないため、
    # genpack/base が virtual/dist-kernel 用に置く kernel-install.py が
    # 発火しない。sys-kernel/catalina-kernel のフックとして中継する
    exeinto /usr/lib/genpack/package-scripts/sys-kernel/catalina-kernel
    doexe "${FILESDIR}/kernel-install.sh"
}
