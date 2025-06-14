EAPI=8

DESCRIPTION="Creates a new PostgreSQL role and a dedicated database"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

RDEPEND="dev-python/psycopg"

S="${WORKDIR}"

src_install() {
    exeinto /usr/bin
    doexe "${FILESDIR}/create-pg-user-and-database.py"
    mv "${D}/usr/bin/create-pg-user-and-database.py" "${D}/usr/bin/create-pg-user-and-database"
}
