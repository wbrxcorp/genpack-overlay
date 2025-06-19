#!/bin/sh
set -e
GCC_VERSION=$(eselect gcc show)
eselect gcc set $GCC_VERSION # create symlinks
