#!/bin/sh
set -e
emaint binhost --fix
emerge -uDN -bk --binpkg-respect-use=y $(ls -1 /etc/portage/sets | sed 's/^/@/') world --keep-going

[ -x /prepare ] && /prepare

emerge -bk --binpkg-respect-use=y @preserved-rebuild
emerge --depclean
etc-update --automode -5
eclean-dist -d
eclean-pkg -d
touch /.done
