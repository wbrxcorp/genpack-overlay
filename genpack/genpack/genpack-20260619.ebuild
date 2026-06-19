EAPI=8

# This ebuild packages the 'genpack' image builder itself inside the target system images (artifacts).
#
# Context:
# While genpack-overlay generally collects ebuilds to act as "components" (such as system services
# or utilities) when building immutable OS images, this specific ebuild is designed to be installed
# inside an artifact image. Installing genpack itself inside the final system allows the running
# immutable OS to self-build new images, provide self-hosting development environments, or compile
# nested OS images directly from within the target platform.

PYTHON_COMPAT=( python3_{13..15} )
inherit python-single-r1 git-r3

DESCRIPTION="OS image builder based on Gentoo Linux"
EGIT_REPO_URI="https://github.com/wbrxcorp/genpack.git"
EGIT_COMMIT="50f24a317934e6dba5089559cf5737e2c1383ff7"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

BDEPEND="
    dev-cpp/argparse
"

RDEPEND="
    dev-python/json5
    dev-python/requests
"

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install || die "emake install failed"
}
