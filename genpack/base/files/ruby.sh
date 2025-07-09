#!/bin/sh
set -e
eselect ruby set $(eselect ruby show | grep '^  ruby')