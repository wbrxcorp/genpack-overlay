EAPI=8

inherit git-r3 autotools systemd

DESCRIPTION="Motion, a software motion detector (live ebuild tracking upstream master)"
HOMEPAGE="https://motion-project.github.io/"
EGIT_REPO_URI="https://github.com/Motion-Project/motion.git"
EGIT_BRANCH="master"

LICENSE="GPL-3+"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE="+webp +opencv +fftw +sqlite pulseaudio alsa mysql mariadb postgres"

RDEPEND="
    acct-group/motion
    acct-user/motion
    media-video/ffmpeg
    media-libs/libv4l
    net-libs/libmicrohttpd

    opencv? ( media-libs/opencv[contribdnn] )
    fftw? ( sci-libs/fftw:3.0 )
    mariadb? ( dev-db/mariadb-connector-c )
    mysql? ( dev-db/mysql-connector-c )
    postgres? ( dev-db/postgresql:= )
    sqlite? ( dev-db/sqlite:3 )
    webp? ( media-libs/libwebp:= )
"

src_prepare() {
        default
        eautoreconf
}

src_configure() {
    econf \
        --sysconfdir=/etc --localstatedir=/var \
        $(use_with opencv) \
        $(use_with fftw fftw3) \
        $(use_with sqlite sqlite3) \
        $(use_with mysql) \
        $(use_with mariadb) \
        $(use_with postgres pgsql) \
        $(use_with webp) \
        $(use_with pulseaudio pulse) \
        $(use_with alsa)
}

src_install() {
        emake \
                DESTDIR="${D}" \
                docdir=/usr/share/doc/${PF} \
                examplesdir=/usr/share/doc/${PF}/examples \
                install

        insinto /etc/motion
        newins data/motion-dist.conf motion.conf

        keepdir /var/lib/motion/media
        fowners -R motion:motion /var/lib/motion
        fperms 0755 /var/lib/motion
        fperms 0775 /var/lib/motion/media

        systemd_newunit "${FILESDIR}/${PN}.service" "${PN}.service"
}