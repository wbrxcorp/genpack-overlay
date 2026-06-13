#!/usr/bin/python3
"""Detect and break known circular dependencies before the main emerge.

Resolves the lower-layer target set with portage's resolver API. portage
reports only the cycle it first gets stuck on, so this works iteratively:
whenever a circular dependency is reported, the breaker USE flags for the
table packages in that cycle are written to a package.use file and the set
is re-resolved, until it resolves cleanly. The cycle-breaking packages are
then emerged (oneshot) so the main emerge can proceed. Does nothing when the
target set resolves cleanly.

The flags are applied per package (via package.use), not as a global USE
value: a table entry like ``media-libs/libavif -gdk-pixbuf`` must only
affect libavif, otherwise disabling such a flag system-wide makes unrelated
packages (every gdk-pixbuf consumer on a desktop) unsatisfiable and the
re-resolution fails for reasons that have nothing to do with the cycle.

Unrecognized command line arguments are passed through to the breaker
emerge (e.g. --jobs, --load-average).

Each resolution runs as a subprocess invocation of this script itself
(--resolve-json mode) so portage reads a fresh config — and thus the
current package.use file — every time.
"""
import os, sys, json, argparse, subprocess

TARGETS = ["@world", "@genpack-runtime", "@genpack-buildtime"]

# Known packages whose USE flags create circular dependencies in the Gentoo
# tree, mapped to the flags to disable on that package while breaking the
# cycle. Applied per package via package.use, so the flags only affect the
# named package.
BREAKER_PACKAGES = {
    "media-libs/freetype":  "-harfbuzz",
    "media-libs/harfbuzz":  "-truetype -cairo",
    "dev-libs/glib":        "-sysprof",
    "media-libs/tiff":      "-webp",
    "media-libs/libwebp":   "-tiff",
    "dev-python/pillow":    "-truetype -tiff -webp -avif",
    "media-libs/libavif":   "-gdk-pixbuf",
    "media-video/ffmpeg":   "-sdl -v4l -svg -pulseaudio -libass -truetype -harfbuzz",
}

# package.use file the breaker writes its per-package overrides to. Sorts
# after genpack's own "genpack" file so it wins for the same atom. Overridable
# for testing. Removed before this script returns so the main emerge is
# unaffected.
BREAKER_PKGUSE = os.environ.get(
    "GENPACK_BREAKER_PKGUSE", "/etc/portage/package.use/zz-genpack-circulardep-breaker")

def log(msg):
    print(f"genpack-break-circular-dep: {msg}", file=sys.stderr)

def resolve_main(targets):
    """Resolve targets and report the result as JSON on stdout."""
    result = {"success": False, "circular": False, "merges": [],
              "cycle_packages": [], "error": None}
    try:
        from _emerge.actions import load_emerge_config
        from _emerge.create_depgraph_params import create_depgraph_params
        from _emerge.depgraph import backtrack_depgraph
        config = load_emerge_config(action="", args=[], opts={})
        myopts = {"--pretend": True, "--update": True, "--deep": True,
                  "--newuse": True, "--usepkg": True}
        params = create_depgraph_params(myopts, "merge")
        success, dg, _favorites = backtrack_depgraph(
            config.target_config.settings, config.trees, myopts, params,
            "merge", targets, None)
        result["success"] = bool(success)
        if success:
            try:
                result["merges"] = [p.cp for p in dg.altlist() if hasattr(p, "cp")]
            except Exception:
                result["success"] = False
        mygraph = dg._dynamic_config._circular_deps_for_display
        result["circular"] = mygraph is not None
        if mygraph is not None:
            # extract the packages actually participating in the cycle(s) from
            # the structured graph portage uses to report them (no string
            # parsing). this is exactly what circular_dependency_handler does in
            # _find_cycles, called directly to avoid its heavy suggestion/
            # autounmask machinery.
            from _emerge.DepPrioritySatisfiedRange import DepPrioritySatisfiedRange
            cps = set()
            for cycle in mygraph.get_cycles(
                    ignore_priority=DepPrioritySatisfiedRange.ignore_medium_soft):
                for node in cycle:
                    if hasattr(node, "cp"):
                        cps.add(node.cp)
            result["cycle_packages"] = sorted(cps)
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    json.dump(result, sys.stdout)
    return 0

def resolve(targets):
    """Resolve in a fresh subprocess so the current package.use is read."""
    cmdline = [sys.executable, os.path.realpath(__file__),
               "--resolve-json", "--targets=" + " ".join(targets)]
    out = subprocess.run(cmdline, stdout=subprocess.PIPE, check=True)
    return json.loads(out.stdout)

def write_breaker_pkguse(pkgs, table):
    """Write per-package USE overrides for the given table packages."""
    os.makedirs(os.path.dirname(BREAKER_PKGUSE), exist_ok=True)
    with open(BREAKER_PKGUSE, "w") as f:
        for pkg in pkgs:
            f.write(f"{pkg} {table[pkg]}\n")

def clear_breaker_pkguse():
    try:
        os.remove(BREAKER_PKGUSE)
    except FileNotFoundError:
        pass

def break_cycles(targets, table, args, emerge_opts):
    # Remove any file left behind by a previously hard-killed run (the finally
    # below covers graceful exits, not SIGKILL/OOM). A stale file would
    # otherwise silently break the first resolution's cycle and hide it.
    clear_breaker_pkguse()

    log(f"checking dependency resolution of {' '.join(targets)} ...")

    # portage reports only the cycle it first gets stuck on, so breaking it can
    # expose another one deeper in the graph. Resolve repeatedly, each pass
    # adding the per-package breaker USE for the table packages in the newly
    # reported cycle, until the target set resolves.
    acted = []          # table packages we will pre-emerge, in table order
    acted_set = set()
    while True:
        r = resolve(targets)
        if r["error"]:
            log(f"resolution failed: {r['error']}")
            return 1
        if r["success"]:
            break
        if not r["circular"]:
            # Not a cycle problem; leave it to the main emerge to report (it
            # will re-hit the original cycle with its canonical message).
            why = "with the breaker USE applied " if acted else ""
            log(f"resolution failed {why}for a reason other than circular "
                "dependencies; leaving it to the main emerge to report.")
            return 0
        cycle_packages = set(r.get("cycle_packages", []))
        if cycle_packages:
            log(f"circular dependencies among: {' '.join(sorted(cycle_packages))}")
            new_pkgs = [p for p in table if p in cycle_packages and p not in acted_set]
        else:
            # cycle membership could not be identified; fall back to applying
            # the remaining table wholesale as a last resort
            new_pkgs = [p for p in table if p not in acted_set]
        if not new_pkgs:
            log("circular dependencies remain but no further breaker-table package "
                "applies; the table needs updating "
                "(or use circulardep_breaker in genpack.json5 as a stopgap).")
            return 1
        for pkg in new_pkgs:
            acted.append(pkg)
            acted_set.add(pkg)
        write_breaker_pkguse(acted, table)
        log("circular dependencies detected. re-resolving with "
            + "; ".join(f"{p} {table[p]}" for p in acted) + " ...")

    if not acted:
        log("no circular dependencies, nothing to do.")
        return 0

    # pre-emerge only the cycle-breaking packages that are actually in the
    # resolved graph (the wholesale fallback above may have added extras)
    merges = set(r["merges"])
    needed = [pkg for pkg in acted if pkg in merges]
    if not needed:
        log("cycles were broken by USE flags alone but no breaker package is part of "
            "the dependency graph; the table may need updating.")
        return 1

    log(f"emerging breaker packages: {' '.join(needed)}")
    # the package.use file is still in effect, so each package builds with its
    # reduced USE; the main emerge later rebuilds them with full USE against
    # the now-installed versions
    emerge_cmd = ["emerge", "--oneshot", "--update", "--buildpkg", "--usepkg",
                  "--binpkg-respect-use=y"]
    if args.pretend:
        emerge_cmd.append("--pretend")
    emerge_cmd += emerge_opts + needed
    subprocess.run(emerge_cmd, check=True)
    log("done.")
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Detect and break known circular dependencies",
        epilog="Unrecognized options are passed through to the breaker emerge.")
    parser.add_argument("--resolve-json", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--pretend", action="store_true", help="Pass --pretend to the breaker emerge (for testing)")
    parser.add_argument("--targets", default=None, help=argparse.SUPPRESS)  # testing
    parser.add_argument("--table-json", default=None, help=argparse.SUPPRESS)  # testing
    args, emerge_opts = parser.parse_known_args()

    targets = args.targets.split() if args.targets else TARGETS
    table = json.loads(args.table_json) if args.table_json else BREAKER_PACKAGES

    if args.resolve_json:
        return resolve_main(targets)

    try:
        return break_cycles(targets, table, args, emerge_opts)
    finally:
        clear_breaker_pkguse()

if __name__ == "__main__":
    sys.exit(main())
