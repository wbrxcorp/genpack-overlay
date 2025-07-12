#!/bin/sh
set -e
# fifos cannot be copied up with overlayfs, so we create them here
if [[ ! -e /var/spool/nullmailer/trigger ]]; then
        mkfifo --mode=0660 "/var/spool/nullmailer/trigger"
fi
chown nullmail:nullmail /var/spool/nullmailer/{tmp,queue,failed,trigger}
chmod 770 /var/spool/nullmailer/{tmp,queue,failed}
chmod 660 /var/spool/nullmailer/trigger

cat <<'EOF' > /usr/lib/systemd/system/nullmailer-smtpd.socket
[Unit]
Description=Nullmailer SMTP socket

[Socket]
ListenStream=[::1]:25
BindIPv6Only=both
Accept=yes

[Install]
WantedBy=sockets.target
EOF

cat <<'EOF' > /usr/lib/systemd/system/nullmailer-smtpd\@.service
[Unit]
Description=Nullmailer SMTPD service (instance %i)
After=nullmailer.service

[Service]
ExecStart=/usr/bin/nullmailer-smtpd
StandardInput=socket
User=nullmail
Group=nullmail
NoNewPrivileges=true
KillMode=process
EOF
