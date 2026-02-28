#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find ELF files in the specified directory")
    parser.add_argument("directory", help="directory to search")
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.directory):
        for f in files:
            path = os.path.join(root, f)
            if not os.path.isfile(path) or os.path.islink(path): continue
            #else
            try:
                with open(path, "rb") as f:
                    if f.read(4) != b"\x7fELF": continue
                #else
                print(path)
            except PermissionError:
                pass