EAPI=8
inherit git-r3

DESCRIPTION="EFI/BIOS bootloader for genpack system.img"
HOMEPAGE="https://github.com/wbrxcorp/genpack-bootloader"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-bootloader.git"
EGIT_COMMIT="2ea0a2ba8c58bef9fbd74ec844cdd5d3dd8e5153"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

BDEPEND="
    amd64? ( sys-boot/grub[grub_platforms_efi-64,grub_platforms_efi-32,grub_platforms_pc] )
    x86? ( sys-boot/grub[grub_platforms_efi-32,grub_platforms_pc] )
    arm64? ( sys-boot/grub[grub_platforms_efi-64] )
    riscv? ( sys-boot/grub[grub_platforms_efi-64] )
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}
