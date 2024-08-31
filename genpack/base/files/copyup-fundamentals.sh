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
