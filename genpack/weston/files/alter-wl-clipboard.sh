#!/bin/sh
if [ ! -x /usr/bin/wl-copy -o ! -x /usr/bin/wl-paste ]; then
    echo "wl-clipboard is not installed"
    exit 1
fi
#else
mv /usr/bin/wl-copy /usr/bin/.wl-copy-orig
mv /usr/bin/wl-paste /usr/bin/.wl-paste-orig
cat << 'EOF' > /usr/bin/wl-copy
#!/bin/sh
exec env WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}" /usr/bin/.wl-copy-orig "$@"
EOF
cat << 'EOF' > /usr/bin/wl-paste
#!/bin/sh
exec env WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}" /usr/bin/.wl-paste-orig "$@"
EOF
chmod +x /usr/bin/wl-copy /usr/bin/wl-paste
