#!/usr/bin/python3
"""Detect and break known circular dependencies before the main emerge.

Resolves the lower-layer target set with portage's resolver API. If a circular
dependency is reported, the breaker USE flags for the *whole* table are written
to a package.use file and the set is re-resolved to confirm the cycles are
gone; then every table package that is part of the graph is emerged (oneshot,
with that package.use still in effect) so it is built as a warm binpkg. The
main emerge afterwards rebuilds those packages with full USE against the
now-installed versions, which it can order freely because warm binpkgs break
build-time cycles. A remaining *non-circular* resolution failure (e.g. a
keyword/USE autounmask change the main emerge handles later) is not the
breaker's concern. Does nothing when the set has no circular dependency.

Why the *whole* table at once rather than only the packages in the reported
cycle -- two properties of portage's resolver, both learned the hard way:

* portage reports only the one cycle it first gets stuck on, and which cycles
  are visible at all depends on the binary-package cache: a package available
  as a USE-matching binpkg is merged with no build step, so its build-time
  edges never enter the graph and any cycle through it is invisible. A
  cache-cold build compiles far more from source and surfaces more cycles.
  There is no reliable "the cycle is X" to react to.

* The reported set also depends on the resolve options and on state: the
  full-set resolve may show only the ffmpeg/libsdl2/pipewire cycle while
  emerging ffmpeg alone pulls a closure that reintroduces the
  docutils/pillow/harfbuzz/glib cycle -- because emerging one package makes
  different binary-vs-source choices than the deep full-set resolve. Applying
  only the cycle portage happened to report therefore leaves other cycles
  unbroken in the pre-emerge closures and the emerge fails.

Applying the whole table sidesteps both: every table flag is a harmless
optional feature disabled only temporarily, so no matter which cycles are
visible or which closure the pre-emerge pulls, they are all broken at once.
This is exactly portage's own advice ("Temporarily changing some use flag for
all packages might be the better option"). The one caveat is that a table
entry must not disable a flag that some package in the graph *hard-requires*
(see the freetype/harfbuzz note on the table) -- that would make the whole set
unsatisfiable; keep the table free of such entries.

The flags are applied per package (via package.use), not as a global USE
value: a table entry like ``media-libs/libavif -gdk-pixbuf`` must only affect
libavif, otherwise disabling such a flag system-wide makes unrelated packages
(every gdk-pixbuf consumer on a desktop) unsatisfiable.

Unrecognized command line arguments are passed through to the breaker emerge
(e.g. --jobs, --load-average).

Each resolution runs as a subprocess invocation of this script itself
(--resolve-json mode) so portage reads a fresh config — and thus the current
package.use file — every time.
"""
import os, sys, json, argparse, subprocess

TARGETS = ["@world", "@genpack-runtime", "@genpack-buildtime"]

# Known packages whose USE flags create circular dependencies in the Gentoo
# tree, mapped to the flags to disable on that package while breaking the
# cycle. Applied per package via package.use, so the flags only affect the
# named package. The whole table is applied at once (see the module docstring),
# so every entry here must be safe to disable across the whole graph: it must
# not disable a flag that some package hard-requires.
#
# History / where to add things: before this breaker existed, each artifact set
# its own packages + minus-USE by hand in the "circulardep_breaker" genpack.json5
# property, applied wholesale (as a global USE). We tried to be cleverer here --
# detect the exact reported cycle and disable only the flags for its packages --
# but portage makes that unworkable: it reports only the one cycle it first gets
# stuck on, which cycles are even visible depends on the binpkg cache, and the
# detection resolve does not make the same binary-vs-source choices as the
# pre-emerge, so a surgically "clean" resolve still hits a cycle when emerged.
# So this returned to wholesale application -- but per-package (not global USE),
# from a shared table (not per-artifact), and gated on a cycle actually being
# present. Division of labour: this table = common, cross-artifact cycles broken
# automatically; genpack.json5 "circulardep_breaker" = the per-artifact escape
# hatch for one-offs not worth generalising here. Prefer adding a genuinely
# shared cycle-breaker to this table; keep artifact-specific quirks in json5.
#
# Note on freetype/harfbuzz -- why neither carries -truetype and why freetype
# is absent entirely:
#   * freetype[harfbuzz] is a PDEPEND (post-dependency), so portage always
#     orders freetype before harfbuzz on its own; the freetype<->harfbuzz cycle
#     is never a hard build cycle and needs no breaker. freetype therefore has
#     no entry -- and must not: freetype[harfbuzz] is hard-required by consumers
#     like sdl2-ttf/vlc/godot, so "freetype -harfbuzz" applied wholesale would
#     make the graph unsatisfiable whenever one of those is present.
#   * conversely harfbuzz[truetype] hard-requires freetype (DEPEND), and
#     freetype[harfbuzz] (PDEPEND) hard-requires harfbuzz[truetype], so pinning
#     "harfbuzz -truetype" is itself unsatisfiable whenever freetype[harfbuzz]
#     is pulled in (e.g. via fontconfig). harfbuzz's only cycle-relevant flag is
#     -cairo (the real, breakable harfbuzz<->cairo cycle).
BREAKER_PACKAGES = {
    "media-libs/harfbuzz":  "-cairo",
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
                  "--newuse": True, "--usepkg": True,
                  # Let portage backtrack past non-circular autounmask stops
                  # (keyword/USE changes) so it reaches and reports the actual
                  # circular dependencies instead of aborting early. Without
                  # this, an artifact needing e.g. a ~arch keyword unmask makes
                  # the resolver stop before any cycle is ever surfaced.
                  "--autounmask-backtrack": "y"}
        params = create_depgraph_params(myopts, "merge")
        success, dg, _favorites = backtrack_depgraph(
            config.target_config.settings, config.trees, myopts, params,
            "merge", targets, None)
        result["success"] = bool(success)
        # altlist() is available even when resolution ultimately failed for a
        # non-circular reason; capture it regardless so the breaker can still
        # tell which of its table packages are part of the graph in that case.
        try:
            result["merges"] = [p.cp for p in dg.altlist() if hasattr(p, "cp")]
        except Exception:
            if success:
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

    # 1. Does the unmodified set have a circular dependency at all? (A purely
    #    non-circular failure is the main emerge's problem, not ours.)
    r = resolve(targets)
    if r["error"]:
        log(f"resolution failed: {r['error']}")
        return 1
    if not r["circular"]:
        log("no circular dependencies, nothing to do." if r["success"] else
            "resolution failed for a reason other than circular dependencies; "
            "leaving it to the main emerge to report.")
        return 0

    # 2. There is at least one cycle. Rather than chase the single cycle portage
    #    happened to report (which is cache- and option-dependent -- see the
    #    module docstring), apply the whole breaker table at once and confirm it
    #    clears every cycle.
    log("circular dependencies detected; applying breaker USE for the whole "
        "table and re-resolving ...")
    write_breaker_pkguse(list(table), table)
    r = resolve(targets)
    if r["error"]:
        log(f"resolution failed: {r['error']}")
        return 1
    if r["circular"]:
        cyc = " ".join(sorted(set(r.get("cycle_packages", []))))
        log("circular dependencies remain even with the whole breaker table "
            "applied" + (f" (among: {cyc})" if cyc else "") + "; the table needs "
            "updating (or use circulardep_breaker in genpack.json5 as a stopgap).")
        return 1

    # 3. Cycles are gone (r may still report a non-circular failure -- keyword/USE
    #    autounmask, slot conflicts -- which is the main emerge's job). Pre-emerge
    #    every table package present in the graph so it is built as a warm binpkg
    #    with reduced USE; the main emerge then rebuilds it with full USE against
    #    the now-installed version, ordering freely because warm binpkgs break
    #    build-time cycles. Emerging with the whole table still in effect keeps
    #    every pre-emerge closure cycle-free too.
    merges = set(r.get("merges", []))
    needed = [pkg for pkg in table if pkg in merges]
    if not needed:
        log("cycles were broken by USE flags alone but no breaker package is part "
            "of the dependency graph; the table may need updating.")
        return 1

    log(f"emerging breaker packages: {' '.join(needed)}")
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
