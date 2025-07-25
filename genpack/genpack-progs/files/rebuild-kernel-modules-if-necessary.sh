#!/bin/sh
set -e
if [ ! -d /usr/src/linux ]; then
    echo "No kernel source found in /usr/src/linux. skipping"
    exit 0
fi
#else
if [ -f /usr/src/linux/.modules-rebuilt-by-genpack ]; then
    echo "Kernel modules already rebuilt by genpack. skipping"
    exit 0
fi
#else
emerge @module-rebuild
touch /usr/src/linux/.modules-rebuilt-by-genpack
echo "Kernel modules rebuilt."

