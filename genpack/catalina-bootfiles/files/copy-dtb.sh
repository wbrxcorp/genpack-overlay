#!/bin/sh
# extlinux.conf の fdt 行はブートパーティションルート(=イメージの/boot)基準なので、
# kernel-build eclass が /lib/modules/<ver>/dtb/ 配下に置く DTB を /boot へ複製する
set -e
dtb=$(ls -t /lib/modules/*/dtb/freescale/imx95-catalina-gw92xx-0x.dtb 2>/dev/null | head -1)
if [ -z "$dtb" ]; then
    echo "Catalina DTB not found under /lib/modules" >&2
    exit 1
fi
cp -v "$dtb" /boot/
