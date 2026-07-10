EAPI=8

DESCRIPTION="stuffs for system.img"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE="baremetal"

# baremetal時のfirmware選択依存について:
# 汎用ベアメタルではsys-kernel/linux-firmwareが必要だが、対象ハードウェアが固定される
# SBCではほぼ全てが無駄なブロブになるため、各SBCプロファイルが必ず導入する小さな
# ボード固有パッケージでもこの依存を満たせるよう||に列挙している。
#   - raspberrypi: sys-firmware/raspberrypi-wifi-ucode
#   - catalina:    genpack/catalina-bootfiles (Catalina基板はカーネルがロードする
#     firmwareブロブを必要としないことを実機確認済み(2026-07)。専用の空firmware
#     パッケージを作る代わりにブートファイルパッケージを代表として使う)
RDEPEND="
	genpack/base
	!genpack/paravirt
	genpack/genpack-install
	sys-apps/kbd
	baremetal? (
		|| ( sys-kernel/linux-firmware sys-firmware/raspberrypi-wifi-ucode genpack/catalina-bootfiles )
		sys-fs/lsscsi
		sys-apps/lshw
		sys-apps/hwloc
		sys-apps/usbutils
		sys-apps/pciutils
		sys-apps/dmidecode
		sys-apps/lm-sensors
		sys-apps/usb_modeswitch
		sys-power/cpupower
		sys-apps/smartmontools
		sys-apps/nvme-cli
		sys-apps/hdparm
		sys-apps/ethtool
		amd64? ( 
			app-misc/beep
			sys-apps/msr-tools 
			sys-apps/memtest86+
		)
	)
"

S="${WORKDIR}"

src_install() {
	# configuration scripts called by systemimg-init
	insinto /usr/lib/genpack-init
	doins "${FILESDIR}/autologin.py" "${FILESDIR}/hostname.py" "${FILESDIR}/install_memtest86.py" "${FILESDIR}/swapfile.py"

	# enable getty@tty1
	exeinto /usr/lib/genpack/package-scripts/sys-apps/systemd
	doexe "${FILESDIR}/enable-getty-at-tty1.sh"

	# enable serial getty@ttyS0 only if ttyS0 is usable
	insinto /etc/systemd/system/serial-getty@ttyS0.service.d
	doins "${FILESDIR}/10-disable-broken-tty.conf"

	exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
	doexe "${FILESDIR}/systemimg.sh"

	exeinto /usr/lib/genpack/package-scripts/sys-kernel/raspberrypi-image
	doexe "${FILESDIR}/raspberrypi-generate-initramfs.py"
}
