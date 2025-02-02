EAPI=8
inherit git-r3

DESCRIPTION="EFI bootloader for genpack system.img"
HOMEPAGE="https://github.com/wbrxcorp/genpack-efiboot"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-efiboot.git"
EGIT_COMMIT="a1c142af3c9fe0cb2b261eaf20da34d4af7ecc64"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

BDEPEND="
    amd64? ( sys-boot/grub[grub_platforms_efi-64,grub_platforms_efi-32] )
    arm64? ( sys-boot/grub[grub_platforms_efi-64] )
    riscv? ( sys-boot/grub[grub_platforms_efi-64] )
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" install || die "emake install failed"
}
