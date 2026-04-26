#!/bin/sh
if [ ! -f /etc/cloudflared/config.yml ]; then
    mkdir -p /etc/cloudflared
    echo "edge-ip-version: auto" > /etc/cloudflared/config.yml
fi
