EAPI=8

PYTHON_COMPAT=( python3_{13..15} )

inherit git-r3
inherit python-single-r1

DESCRIPTION="Convert the IPsum blocklist to nftables"
HOMEPAGE="https://github.com/shimarin/ipsum2nft"
LICENSE="MIT"
EGIT_REPO_URI="https://github.com/shimarin/ipsum2nft.git"
EGIT_COMMIT="176ccc8c608e5d120177e8bd30a689b942115f71"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"
IUSE=""

RDEPEND="${PYTHON_DEPS}
	net-firewall/nftables
"

src_prepare() {
	default
	# The unit hardcodes the binary path for the Makefile's default
	# PREFIX (/usr/local); we install to /usr.
	sed -i -e 's|/usr/local/bin/ipsum2nft|/usr/bin/ipsum2nft|' \
		ipsum2nft.service || die
}

src_compile() {
	# Pure Python script; nothing to compile. Explicit no-op so the
	# default src_compile does not run the Makefile's default (install)
	# target without DESTDIR.
	:
}

src_install() {
	# The units ship as part of the OS image, so install them into the
	# vendor unit directory rather than /etc/systemd/system.
	emake DESTDIR="${D}" PREFIX="/usr" UNITDIR="/usr/lib/systemd/system" \
		install || die "emake install failed"
}
