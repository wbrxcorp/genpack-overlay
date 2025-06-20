#!/bin/sh
set -e
JAVA_VM=$(eselect java-vm show system|tail -1|tr -d '[:space:]')
eselect java-vm set system "$JAVA_VM"
ln -s ${JAVA_VM} /usr/lib/jvm/jdk