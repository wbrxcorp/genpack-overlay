EAPI=8

DESCRIPTION="Development GUI tools and utilities launcher"

SLOT="0"
KEYWORDS="amd64 x86 arm64 riscv"

IUSE=""

RDEPEND="
    genpack/devel

    www-client/google-chrome
    gui-apps/waypipe[lz4,zstd]
    media-fonts/noto
    media-fonts/noto-cjk
    media-fonts/noto-emoji
    dev-util/claude-code
    <x11-terms/ghostty-1.2
    gui-libs/gtk[wayland]
    media-sound/alsa-utils
    app-admin/sudo
    sys-process/psmisc
    app-editors/vscode[wayland]
    app-text/xournalpp
    dev-python/pygobject

    app-containers/docker
    app-containers/docker-compose

    app-misc/jq
    dev-python/pip
    sys-apps/fd
    app-text/tree
    sys-apps/bat
    dev-python/pylint
    dev-python/pytest
"

S="${WORKDIR}"

src_install() {
    # Install devlauncher script
    exeinto /usr/bin
    newexe ${FILESDIR}/devlauncher.py devlauncher
}
