#!/bin/sh
set -e

# disable DNSSEC https://www.e-ontap.com/dns/onsenkansai3/
sed -i 's/^#DNSSEC=.*/DNSSEC=no/' /etc/systemd/resolved.conf

systemctl enable systemd-networkd systemd-resolved systemd-timesyncd