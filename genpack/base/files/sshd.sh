#!/bin/sh
cp /usr/lib/genpack/genpack-init-sshd.py /usr/lib/genpack-init/sshd.py
systemctl enable sshd