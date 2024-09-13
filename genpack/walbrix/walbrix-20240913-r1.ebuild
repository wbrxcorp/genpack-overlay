EAPI=8

DESCRIPTION="Basic dependencies for walbrix"

SLOT="0"
KEYWORDS="amd64 arm64 riscv"

RDEPEND="
    arm64? ( sys-kernel/gentoo-kernel[initramfs,savedconfig] )
    riscv? ( sys-kernel/gentoo-kernel[initramfs,savedconfig] )
    amd64? (
        sys-kernel/gentoo-kernel-bin[initramfs]
        app-backup/fsarchiver
        app-crypt/chntpw
        app-crypt/gocryptfs
        app-editors/bvi
        net-misc/ifenslave
        sys-apps/cciss_vol_status
        sys-boot/mokutil
        sys-cluster/drbd-utils
        sys-fs/safecopy
    )
    genpack/systemimg[baremetal]
    app-admin/wbui
"
S="${WORKDIR}"
