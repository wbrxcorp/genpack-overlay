#!/bin/sh
# genpack does not ship net-dns/bind-tools (dropped per Gentoo bug #977172),
# so artifacts pulling in net-dns/doggo get fake nslookup/dig shims for the
# muscle-memory commands. See files/fake-nslookup, files/fake-dig.
cp /usr/lib/genpack/fake-nslookup /usr/bin/nslookup
cp /usr/lib/genpack/fake-dig /usr/bin/dig
chmod 755 /usr/bin/nslookup /usr/bin/dig
