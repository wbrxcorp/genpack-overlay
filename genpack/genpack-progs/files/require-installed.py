#!/usr/bin/env python3

"""Require that the given package atoms are installed; exit non-zero if any are missing."""

from __future__ import annotations

import argparse
import sys

import portage


def check_atoms(atoms: list[str]) -> list[str]:
    vardb = portage.db[portage.root]["vartree"].dbapi
    missing: list[str] = []
    for atom in atoms:
        if not portage.isvalidatom(atom):
            print(f"error: invalid atom: {atom!r}", file=sys.stderr)
            sys.exit(2)
        if not vardb.match(atom):
            missing.append(atom)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the given package atoms are installed."
    )
    parser.add_argument("atoms", nargs="+", help="package atom(s) to check")
    args = parser.parse_args()

    missing = check_atoms(args.atoms)
    if missing:
        for atom in missing:
            print(f"error: not installed: {atom}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
