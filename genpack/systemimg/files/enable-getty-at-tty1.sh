#!/bin/sh
set -e
recursive-touch /etc/systemd/system/getty.target.wants/getty\@tty1.service
