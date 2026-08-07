#!/bin/sh
# Wire pam_userdb into the console login stack for /usr/bin/console-passwd.
#
# /etc/pam.d/login belongs to sys-auth/pambase, so this runs as a package-script
# for that package rather than installing a conflicting file from genpack/base.
#
# Both the PAM stack and the (empty) database are rewritten unconditionally
# instead of "only when missing": genpack packs the upper layer alone, so a
# no-op here would leave the change stranded in the lower layer and it would
# never reach the image -- the same trap as the stale systemctl-enable symlinks.
set -e

PAM_LOGIN=/etc/pam.d/login
DB=/etc/console-passwd.db
BEGIN_MARKER="# genpack console-passwd: begin"
END_MARKER="# genpack console-passwd: end"

# A missing pam_userdb.so turns the "default=die" below into "nobody can log in
# at the console at all", and a berkdb-flavoured one cannot read the gdbm
# database we ship. Fail the build rather than shipping such an image.
userdb=""
for dir in /lib/security /lib64/security /usr/lib/security /usr/lib64/security; do
	if [ -e "$dir/pam_userdb.so" ]; then
		userdb="$dir/pam_userdb.so"
		break
	fi
done
if [ -z "$userdb" ]; then
	echo "console-passwd: pam_userdb.so not found" >&2
	exit 1
fi
if ! ldd "$userdb" | grep -q libgdbm; then
	echo "console-passwd: $userdb is not linked against gdbm (sys-libs/pam[berkdb]?)" >&2
	exit 1
fi

# auth_err=die is the point of the whole exercise: once a user has an entry in
# the database, the (possibly stale, possibly empty) hash left in the image's
# /etc/shadow must not be accepted as a second valid password. user_unknown
# keeps everybody else on pam_unix, and pam_env runs up front because
# success=done skips the include below along with its session-independent
# auth-phase setup.
if ! awk -v begin_marker="$BEGIN_MARKER" -v end_marker="$END_MARKER" -v db="$DB" '
$0 == begin_marker { skip = 1; next }
$0 == end_marker { skip = 0; next }
skip { next }
!inserted && /^auth[ \t]/ {
	print begin_marker
	print "auth\t\trequired\tpam_env.so"
	print "auth\t\t[success=done auth_err=die user_unknown=ignore default=die]\tpam_userdb.so db=" db " crypt=crypt"
	print end_marker
	inserted = 1
}
{ print }
END { exit inserted ? 0 : 1 }
' "$PAM_LOGIN" > "$PAM_LOGIN.new"; then
	rm -f "$PAM_LOGIN.new"
	echo "console-passwd: no auth line found in $PAM_LOGIN" >&2
	exit 1
fi
chmod 644 "$PAM_LOGIN.new"
mv "$PAM_LOGIN.new" "$PAM_LOGIN"

# pam_userdb reports a missing database as a system error, which default=die
# turns into a total lockout, so a fresh deployment needs an empty database in
# the image: no entries means everyone falls through to pam_unix as before.
python3 -c 'import dbm.gnu, os, sys
path = sys.argv[1]
dbm.gnu.open(path, "n", 0o600).close()
os.chmod(path, 0o600)
os.chown(path, 0, 0)' "$DB"
