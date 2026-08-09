#!/bin/sh
set -e
recursive-touch /etc/passwd /etc/group /etc/shadow /etc/profile.env
recursive-touch /etc/ld.so.conf /etc/ld.so.conf.d/*
recursive-touch /usr/lib/locale/locale-archive
recursive-touch /usr/bin/sed /usr/bin/awk /bin/nano \
        /usr/bin/tar \
        /usr/bin/wget \
        /usr/bin/make /usr/bin/diff /usr/bin/patch /usr/bin/strings /usr/bin/strace \
        /usr/bin/find /usr/bin/xargs /usr/bin/less \
        /usr/bin/locale-gen

# remove root password
sed -i 's/^root:\*:/root::/' /etc/shadow

# empty iptables/nftables rules
if [ -d /var/lib/iptables ]; then
        touch /var/lib/iptables/rules-save
fi
if [ -d /var/lib/ip6tables ]; then
        touch /var/lib/ip6tables/rules-save
fi
if [ -d /var/lib/nftables ]; then
        touch /var/lib/nftables/rules-save
fi

# update mime database
if [ -d /usr/share/mime -a -x /usr/bin/update-mime-database ]; then
        update-mime-database /usr/share/mime
fi

if [ -d /usr/share/applications -a -x /usr/bin/update-desktop-database ]; then
        update-desktop-database
fi

# unify LANG into /etc/environment
#
# /etc/environment is the one file that reaches console logins, ssh logins
# (both through `session required pam_env.so` in system-auth, which
# system-login includes *after* its own envfile=/etc/profile.env line and which
# therefore wins) and systemd user instances (through the
# /usr/lib/environment.d/99-environment.conf -> /etc/environment compat
# symlink).  System services keep reading /etc/locale.conf instead; the
# genpack-init locale scripts write both.
#
# pam_env reads /etc/environment when it exists and falls back to the vendor
# copy in /usr/share/pam/environment otherwise (Linux-PAM 1.7 vendordir, which
# is why no package owns /etc/environment any more).  That is a fallback and not
# a merge, so seed from the vendor file rather than shadowing whatever it holds.
if [ ! -f /etc/environment ] && [ -f /usr/share/pam/environment ]; then
        cp /usr/share/pam/environment /etc/environment
fi

# env-update leaves LANG in /etc/profile.env, and /etc/profile sources that
# unconditionally after PAM has run, so the line there would override
# /etc/environment in login shells.  Move the value over and delete the line.
# Deleting rather than commenting out: nothing reads a commented line, and it
# only invites someone to uncomment it later.
lang=$(sed -n "s/^export LANG='\(.*\)'\$/\1/p" /etc/profile.env)
if [ -n "$lang" ]; then
        touch /etc/environment
        sed -i '/^LANG=/d' /etc/environment
        echo "LANG=$lang" >> /etc/environment
fi
sed -i '/^export LANG=/d' /etc/profile.env

# copyup gcc libraries
touch -ha `gcc --print-file-name=`/*.so.* && ldconfig

for i in versions.py __init__.py installation.py const.py eapi.py exception.py localization.py; do
	recursive-touch /usr/lib/python*/site-packages/portage/$i
done

recursive-touch /usr/lib/python*/site-packages/portage/proxy/*.py