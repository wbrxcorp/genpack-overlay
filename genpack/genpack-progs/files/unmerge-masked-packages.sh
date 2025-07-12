#!/bin/sh
equery list -F '$cpv,$mask' '*'|grep -e ',M *$' > /tmp/all-packages
# if grep fails, it means no masked packages
if [ $? -ne 0 ]; then
    echo "No masked packages found."
    exit 0
fi
# else
set -e
cat /tmp/all-packages | sed 's/^\(.*\),.*/=\1/'|xargs emerge --unmerge
emerge -bk -uDN --with-bdeps=y --keep-going @world
