#!/bin/sh
set -e
case "$(uname -m)" in
    x86_64)
        ARCH="amd64"
        ;;
    aarch64)
        ARCH="arm64"
        ;;
    *)
        echo "Unsupported architecture"
        exit 1
        ;;
esac

echo "Installing cloudflared"

TMPFILE=/tmp/cloudflared-$$
curl -L --output $TMPFILE https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$ARCH
chmod +x $TMPFILE
mkdir -p /usr/local/bin
mv $TMPFILE /usr/local/bin/cloudflared

if [ ! -f /etc/cloudflared/config.yml ]; then
    mkdir -p /etc/cloudflared
    echo "edge-ip-version: auto" > /etc/cloudflared/config.yml
fi

echo
echo "Cloudflared installed"
echo "'cloudflared service install TOKEN' to install cloudflared as a service"
echo "'systemctl enable cloudflared-update.timer; systemctl start cloudflared-update.timer' to enable automatic updates"
