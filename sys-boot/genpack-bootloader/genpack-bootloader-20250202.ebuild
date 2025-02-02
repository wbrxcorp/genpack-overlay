EAPI=8
inherit git-r3

DESCRIPTION="EFI/BIOS bootloader for genpack system.img"
HOMEPAGE="https://github.com/wbrxcorp/genpack-bootloader"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack-bootloader.git"
EGIT_COMMIT="a1d999ba0e175be1ab393a2da0f1e1a8186c1095"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

BDEPEND="
    amd64? ( sys-boot/grub[grub_platforms_efi-64,grub_platforms_efi-32,grub_platforms_pc] )
    arm64? ( sys-boot/grub[grub_platforms_efi-64] )
    riscv? ( sys-boot/grub[grub_platforms_efi-64] )
"

src_compile() {
    emake || die "emake failed"
}

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}
