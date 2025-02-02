#!/usr/bin/python3
import subprocess,os

def get_all_sets():
    sets_dir = '/etc/portage/sets'
    if not os.path.exists(sets_dir): return []
    #else
    return ['@' + f for f in os.listdir(sets_dir)]

def is_executable(path):
    return os.path.exists(path) and os.access(path, os.X_OK)

def main(disable_using_binpkg):
    subprocess.run(['emaint', 'binhost', '--fix'], check=True)
    all_sets = get_all_sets()
    if disable_using_binpkg:
        subprocess.run(['emerge', '-uDN', '-b', '--usepkg=n'] + all_sets + ['world', '--keep-going'], check=True)
    else:
        subprocess.run(['emerge', '-uDN', '-bk', '--binpkg-respect-use=y'] + all_sets + ['world', '--keep-going'], check=True)
    if is_executable('/prepare'):
        if disable_using_binpkg: os.environ['DISABLE_USING_BINPKG'] = '1'
        subprocess.run(['/prepare'], check=True)
    if disable_using_binpkg:
        subprocess.run(['emerge', '-b', '--usepkg=n', '@preserved-rebuild'], check=True)
    else:
        subprocess.run(['emerge', '-bk', '--binpkg-respect-use=y', '@preserved-rebuild'], check=True)

    subprocess.run(['emerge', '--depclean'], check=True)
    subprocess.run(['etc-update', '--automode', '-5'], check=True)
    subprocess.run(['eclean-dist', '-d'], check=True)
    subprocess.run(['eclean-pkg', '-d'], check=True)
    subprocess.run(['check-unwanted-pythons'], check=True)
    open('/.done', 'w').close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable-using-binpkg', action='store_true')
    args = parser.parse_args()
    try:
        main(args.disable_using_binpkg)
    except subprocess.CalledProcessError as e:
        exit(e.returncode) # exit with the same return code as the failed command
