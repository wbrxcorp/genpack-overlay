#!/bin/sh
set -e
BINUTILS_VERSION=$(eselect binutils show)
eselect binutils set $BINUTILS_VERSION # create symlinks
