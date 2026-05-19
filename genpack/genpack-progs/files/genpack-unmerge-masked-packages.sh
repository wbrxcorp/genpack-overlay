#!/bin/sh
# Usage: genpack-unmerge-masked-packages [emerge-opts...]
# Extra arguments (e.g. --jobs=N --load-average=N) are forwarded to the
# @world rebuild emerge invocation.
equery list -F '$cpv,$mask' '*'|grep -e ',M *$' > /tmp/all-packages
if [ $? -ne 0 ]; then
    echo "No masked packages found."
    exit 0
fi
set -e
cat /tmp/all-packages | sed 's/^\(.*\),.*/=\1/'|xargs emerge --unmerge
emerge -bk -uDN --with-bdeps=y --keep-going "$@" @world
