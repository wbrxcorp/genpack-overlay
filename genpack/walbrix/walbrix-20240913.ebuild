EAPI=8

DESCRIPTION="Basic dependencies for walbrix"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

RDEPEND="
    amd64? ( sys-kernel/gentoo-kernel-bin[initramfs] )
    arm64? ( sys-kernel/gentoo-kernel[initramfs,savedconfig] )
    genpack/systemimg[baremetal]
    app-admin/wbui
"
S="${WORKDIR}"
