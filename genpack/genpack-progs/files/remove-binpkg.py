#!/usr/bin/env python3

"""Remove Portage binary packages by atom."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import portage


BINPKG_SUFFIXES = (".gpkg.tar", ".tbz2", ".xpak")


def get_default_pkgdir() -> Path:
    result = subprocess.run(
        ["portageq", "pkgdir"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def refresh_binhost_index(pkgdir: Path) -> None:
    env = dict(os.environ)
    env["PKGDIR"] = str(pkgdir)
    subprocess.run(["emaint", "binhost", "--fix"], check=True, env=env)


def split_supported_atom(raw_atom: str) -> tuple[str, str | None]:
    atom = raw_atom.strip()
    if not portage.isvalidatom(atom):
        raise ValueError(f"invalid atom: {raw_atom}")

    if atom[:1] in {"<", ">"} or atom.startswith("~"):
        raise ValueError(
            "range atoms are not supported; use cat/pkg or =cat/pkg-version"
        )

    exact = atom.startswith("=")
    normalized = atom[1:] if exact else atom
    cp = portage.dep.dep_getkey(atom)

    if normalized == cp:
        return cp, None

    prefix = f"{cp}-"
    if not normalized.startswith(prefix):
        raise ValueError(
            "unsupported atom form; use cat/pkg or =cat/pkg-version"
        )

    if not exact:
        raise ValueError(
            "versioned atoms must use the exact form: =cat/pkg-version"
        )

    version = normalized[len(prefix) :]
    if not version:
        raise ValueError("missing version in exact atom")

    return cp, version


def strip_binpkg_suffix(name: str) -> str | None:
    for suffix in BINPKG_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return None


def find_matches(pkgdir: Path, cp: str, exact_version: str | None) -> list[Path]:
    category, pn = cp.split("/", 1)
    category_dir = pkgdir / category
    if not category_dir.is_dir():
        return []

    matches: list[Path] = []
    exact_pf = f"{pn}-{exact_version}" if exact_version else None
    package_dir = category_dir / pn

    if package_dir.is_dir():
        candidates = sorted(package_dir.rglob("*"))
    else:
        candidates = sorted(category_dir.rglob("*"))

    for entry in candidates:
        if not entry.is_file():
            continue

        stem = strip_binpkg_suffix(entry.name)
        if stem is None:
            continue

        if not stem.startswith(f"{pn}-"):
            continue

        if exact_pf is not None and stem != exact_pf and not stem.startswith(f"{exact_pf}-"):
            continue

        matches.append(entry)

    return matches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List or remove matching Portage binary package files."
    )
    parser.add_argument(
        "atoms",
        nargs="+",
        help="package atom(s): cat/pkg or =cat/pkg-version",
    )
    parser.add_argument(
        "--pkgdir",
        type=Path,
        default=None,
        help="override PKGDIR (defaults to `portageq pkgdir`)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="actually delete the matching files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pkgdir = args.pkgdir or get_default_pkgdir()
    matches: list[Path] = []
    seen: set[Path] = set()

    for atom in args.atoms:
        try:
            cp, exact_version = split_supported_atom(atom)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        atom_matches = find_matches(pkgdir, cp, exact_version)
        if not atom_matches:
            print(f"no matching binary packages found in {pkgdir} for {atom}")
            continue

        for path in atom_matches:
            if path in seen:
                continue
            seen.add(path)
            matches.append(path)

    if not matches:
        return 1

    action = "deleting" if args.delete else "would delete"
    print(f"{action} {len(matches)} file(s) from {pkgdir}:")
    for path in matches:
        print(path)

    if not args.delete:
        print("dry-run only; pass --delete to remove these files")
        return 0

    failures = 0
    for path in matches:
        try:
            path.unlink()
        except OSError as exc:
            failures += 1
            print(f"failed to delete {path}: {exc}", file=sys.stderr)

    if failures:
        return 1

    print("done")
    print("refreshing binhost index with `emaint binhost --fix`...")
    refresh_binhost_index(pkgdir)
    print("binhost index refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
