"""Shared helpers for the genpack-init scripts in /usr/lib/genpack-init.

genpack-init loads every script there with SourceFileLoader under one and the
same module name, and does not put that directory on sys.path, so the scripts
cannot import each other.  Code shared between them goes here instead: this
module is installed into the site-packages of the very interpreter genpack-init
embeds, so a plain import works from any script.

Deliberately not named genpack_init: genpack-init registers a C++ extension
module under that name in sys.modules before loading any script, and it would
shadow anything of the same name in site-packages.
"""
import os, re

def merge_env_file(path, name, value):
    """Set name=value in a KEY=VALUE file, replacing any entry already there.

    Written for /etc/environment and /etc/locale.conf.  Values are emitted bare,
    without quotes and without export, which is what every reader of those two
    accepts: pam_env, systemd's environment.d parser (which reaches
    /etc/environment through the 99-environment.conf compat symlink) and
    systemd's locale.conf reader.  An export prefix in particular would make
    environment.d read "export LANG" as the variable name.

    Only the matching line is touched, so variables an end user added to
    /etc/environment survive.  Rewriting in place rather than appending matters
    because the callers run on every boot, and appending would add a line each
    time.
    """
    pattern = re.compile(rf'^\s*(?:export\s+)?{re.escape(name)}\s*=')
    lines = []
    if os.path.isfile(path):
        with open(path) as f:
            lines = [line for line in f.read().splitlines() if not pattern.match(line)]
    lines.append(f"{name}={value}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
