#!/bin/sh
# /boot/kernel・/boot/initramfs symlink を作る kernel-install.py は
# package-scripts/virtual/dist-kernel/ に置かれているが、virtual/dist-kernel の
# プロバイダは gentoo-kernel 系限定(かつバージョン連動)なので catalina-kernel では
# インストールされず、package-script機構から実行されない。
# 代わりに sys-kernel/catalina-kernel のフックとして同じ処理を発火させる。
exec /usr/lib/genpack/package-scripts/virtual/dist-kernel/kernel-install.py
