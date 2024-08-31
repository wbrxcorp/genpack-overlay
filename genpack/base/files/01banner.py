import os

def configure(ini):
    banner_file = "/.genpack/banner"
    if os.path.isfile(banner_file):
        with open(banner_file) as f:
            print(f.read())


