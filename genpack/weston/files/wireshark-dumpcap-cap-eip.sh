#!/bin/sh
set -e
if [ ! -x /usr/bin/dumpcap ]; then
    echo "wireshark is not installed"
    exit 1
fi
#else
setcap 'cap_net_raw,cap_net_admin=eip' /usr/bin/dumpcap
