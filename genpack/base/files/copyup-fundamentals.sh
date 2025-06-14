#!/bin/sh
recursive-touch /etc/passwd /etc/group /etc/shadow /etc/profile.env
recursive-touch /etc/ld.so.conf /etc/ld.so.conf.d/*
recursive-touch /usr/lib/locale/locale-archive
recursive-touch /usr/bin/sh /usr/bin/sed /usr/bin/awk /usr/bin/python /bin/nano \
        /usr/bin/tar /usr/bin/unzip \
        /usr/bin/wget /usr/bin/curl /usr/bin/telnet \
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

# set locale conf to pam env
sed -i 'r"s/^export LANG=\(.*\)$/#export LANG=\1 # apply \/etc\/locale.conf instead/' /etc/profile.env
sed -i 'r"/^session\t\+required\t\+pam_env\.so envfile=\/etc\/profile\.env$/a session\t\trequired\tpam_env.so envfile=\/etc\/locale.conf' /etc/pam.d/system-login

# copyup gcc libraries
touch -ha `gcc --print-file-name=`/*.so.* && ldconfig

for i in versions.py __init__.py installation.py const.py eapi.py exception.py localization.py; do
	recursive-touch /usr/lib/python*/site-packages/portage/$i
done

recursive-touch /usr/lib/python*/site-packages/portage/proxy/*.py