#!/bin/sh
set -e
# disable becoming root with empty password
sed -Ei '/^[[:space:]]*auth[[:space:]]+include[[:space:]]+system-auth([[:space:]]|$)/i auth   required   pam_unix.so try_first_pass' /usr/lib/pam.d/polkit-1
