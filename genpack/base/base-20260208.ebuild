EAPI=8

DESCRIPTION="base system"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

IUSE="+vi +strace +btrfs +xfs +wireguard +cron +audit +logrotate +sshd +tcpdump +banner +install-cloudflared"

REQUIRED_USE="
    logrotate? ( cron )
"

RDEPEND="
    || ( sys-kernel/gentoo-kernel-bin[initramfs] sys-kernel/gentoo-kernel[initramfs] sys-kernel/raspberrypi-image )
    sys-kernel/dracut-genpack
    sys-apps/genpack-init
    sys-apps/gentoo-systemd-integration
    sys-libs/timezone-data
    app-alternatives/sh
    sys-apps/net-tools
    app-arch/gzip
    app-arch/unzip
    dev-lang/python
    dev-python/requests
    sys-apps/grep
    app-misc/ca-certificates
    sys-apps/coreutils
    sys-process/procps
	sys-apps/which
    net-misc/rsync
    net-misc/iputils
    sys-apps/iproute2
    tcpdump? ( net-analyzer/tcpdump )
    sshd? ( net-misc/openssh )
    vi? ( app-editors/vim )
    strace? ( dev-debug/strace )
    wireguard? ( net-vpn/wireguard-tools net-vpn/wg-genconf )
    btrfs? ( sys-fs/btrfs-progs )
    xfs? ( sys-fs/xfsprogs )
    cron? ( sys-process/cronie )
    audit? ( sys-process/audit )
    logrotate? ( app-admin/logrotate )
"

S="${WORKDIR}"

src_prepare() {
    default
    # files/foo.cpp -> ${S}/foo.cpp にコピー
    cp "${FILESDIR}"/shutdown.cpp "${S}"/ || die
}

src_compile() {
    # 必要なら CPPFLAGS を前に、LDFLAGS を後ろに
    g++ shutdown.cpp -o genpack-shutdown -static || die "compile failed"
}

src_install() {
    # install shutdown program
    exeinto /usr/libexec
    doexe genpack-shutdown

    # script for genpack
    exeinto /usr/lib/genpack/package-scripts/${CATEGORY}/${PN}
    doexe "${FILESDIR}/copyup-fundamentals.sh"

    exeinto /usr/lib/genpack/package-scripts/sys-libs/glibc
    doexe "${FILESDIR}/locale-gen.sh"

    exeinto /usr/lib/genpack/package-scripts/virtual/dist-kernel
    doexe "${FILESDIR}/kernel-install.py"
    use banner && doexe "${FILESDIR}/generate-default-banner.sh"

    exeinto /usr/lib/genpack/package-scripts/sys-apps/systemd
    doexe "${FILESDIR}/systemd.sh"

    exeinto /usr/lib/genpack/package-scripts/net-firewall/iptables
    doexe "${FILESDIR}/iptables-set-legacy.sh"

    insinto /usr/lib/genpack
    doins "${FILESDIR}/genpack-init-docker.py"
    doins "${FILESDIR}/genpack-init-mysql.py"
    doins "${FILESDIR}/genpack-init-sshd.py"

    exeinto /usr/lib/genpack/package-scripts/sys-auth/polkit
    doexe "${FILESDIR}/polkit.sh"

    exeinto /usr/lib/genpack/package-scripts/app-containers/docker
    doexe "${FILESDIR}/docker.sh"

    exeinto /usr/lib/genpack/package-scripts/dev-db/mysql
    doexe "${FILESDIR}/mysql.sh"

    exeinto /usr/lib/genpack/package-scripts/dev-db/postgresql
    doexe "${FILESDIR}/postgresql.sh"

    exeinto /usr/lib/genpack/package-scripts/dev-lang/php
    doexe "${FILESDIR}/php.sh"

    exeinto /usr/lib/genpack/package-scripts/sys-devel/gcc
    doexe "${FILESDIR}/gcc.sh"

    exeinto /usr/lib/genpack/package-scripts/sys-devel/binutils
    doexe "${FILESDIR}/binutils.sh"

    exeinto /usr/lib/genpack/package-scripts/virtual/jdk
    doexe "${FILESDIR}/java.sh"

    exeinto /usr/lib/genpack/package-scripts/www-servers/apache
    doexe "${FILESDIR}/apache.sh"

    exeinto /usr/lib/genpack/package-scripts/dev-lang/ruby
    doexe "${FILESDIR}/ruby.sh"

    exeinto /usr/lib/genpack/package-scripts/media-fonts/noto-cjk
    doexe "${FILESDIR}/noto-cjk.sh"

    exeinto /usr/lib/genpack/package-scripts/mail-mta/nullmailer
    doexe "${FILESDIR}/nullmailer.sh"

    exeinto /usr/lib/genpack/package-scripts/acct-user/zabbix
    doexe "${FILESDIR}/allow-zabbix-user-reading-journal.sh"

    if use cron; then
        exeinto /usr/lib/genpack/package-scripts/sys-process/cronie
        doexe "${FILESDIR}/cron.sh"
    fi
    if use audit; then
        exeinto /usr/lib/genpack/package-scripts/sys-process/audit
        doexe "${FILESDIR}/audit.sh"
    fi
    if use sshd; then
        exeinto /usr/lib/genpack/package-scripts/net-misc/openssh
        doexe "${FILESDIR}/sshd.sh"
    fi
    if use vi; then
        exeinto /usr/lib/genpack/package-scripts/app-editors/vim
        doexe "${FILESDIR}/vim.sh"
    fi

    exeinto /usr/bin
    newexe "${FILESDIR}/glsa-check.py" genpack-glsa-check

    insinto /usr/lib/genpack-init
    use banner && doins "${FILESDIR}/01banner.py"
    newins "${FILESDIR}/genpack-init-timezone.py" timezone.py
    newins "${FILESDIR}/genpack-init-locale.py" locale.py
    doins "${FILESDIR}/generate-machine-id.py"

    exeinto /usr/bin
    use install-cloudflared && newexe "${FILESDIR}/install-cloudflared.sh" install-cloudflared
}
