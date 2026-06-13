#!/usr/bin/python3
"""Detect and break known circular dependencies before the main emerge.

Resolves the lower-layer target set with portage's resolver API. If the
resolution fails due to circular dependencies, re-resolves with the
breaker USE flags below applied, then emerges (oneshot) the breaker
packages that actually appear in the dependency graph so the main emerge
can proceed. Does nothing when the target set resolves cleanly.

Unrecognized command line arguments are passed through to the breaker
emerge (e.g. --jobs, --load-average).

The resolver honors the USE environment variable only when it is set
before portage is imported, so resolutions run as subprocess invocations
of this script itself (--resolve-json mode).
"""
import os, sys, json, argparse, subprocess

TARGETS = ["@world", "@genpack-runtime", "@genpack-buildtime"]

# Known packages whose USE flags create circular dependencies in the Gentoo
# tree, and the flags to disable while breaking the cycle. The flags of all
# entries are combined into a single USE value; per-package attribution is
# for maintainability only.
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

def log(msg):
    print(f"genpack-break-circular-dep: {msg}", file=sys.stderr)

def resolve_main(targets, use):
    """Resolve targets and report the result as JSON on stdout."""
    if use is not None:
        os.environ["USE"] = use
    # portage must be imported after USE is finalized
    result = {"success": False, "circular": False, "merges": [], "error": None}
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
        result["circular"] = dg._dynamic_config._circular_deps_for_display is not None
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    json.dump(result, sys.stdout)
    return 0

def resolve(targets, use=None):
    cmdline = [sys.executable, os.path.realpath(__file__),
               "--resolve-json", "--targets=" + " ".join(targets)]
    if use is not None:
        cmdline.append("--use=" + use)
    out = subprocess.run(cmdline, stdout=subprocess.PIPE, check=True)
    return json.loads(out.stdout)

def main():
    parser = argparse.ArgumentParser(
        description="Detect and break known circular dependencies",
        epilog="Unrecognized options are passed through to the breaker emerge.")
    parser.add_argument("--resolve-json", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--use", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--pretend", action="store_true", help="Pass --pretend to the breaker emerge (for testing)")
    parser.add_argument("--targets", default=None, help=argparse.SUPPRESS)  # testing
    parser.add_argument("--table-json", default=None, help=argparse.SUPPRESS)  # testing
    args, emerge_opts = parser.parse_known_args()

    targets = args.targets.split() if args.targets else TARGETS
    table = json.loads(args.table_json) if args.table_json else BREAKER_PACKAGES

    if args.resolve_json:
        return resolve_main(targets, args.use)

    log(f"checking dependency resolution of {' '.join(targets)} ...")
    r = resolve(targets)
    if r["error"]:
        log(f"resolution failed: {r['error']}")
        return 1
    if r["success"]:
        log("no circular dependencies, nothing to do.")
        return 0
    if not r["circular"]:
        log("resolution failed for a reason other than circular dependencies; "
            "leaving it to the main emerge to report.")
        return 0

    # combine breaker USE flags of all entries, preserving order
    use_flags = []
    for flags in table.values():
        for f in flags.split():
            if f not in use_flags:
                use_flags.append(f)
    use = " ".join(use_flags)
    log(f"circular dependencies detected. re-resolving with USE=\"{use}\" ...")

    r = resolve(targets, use)
    if r["error"]:
        log(f"resolution failed: {r['error']}")
        return 1
    if not r["success"]:
        if r["circular"]:
            log("circular dependencies remain even with all breaker USE flags applied. "
                "The breaker package table of this script needs updating "
                "(or use circulardep_breaker in genpack.json5 as a stopgap).")
        else:
            log("resolution with breaker USE flags failed for another reason; "
                "leaving it to the main emerge to report.")
        return 1

    merges = set(r["merges"])
    needed = [pkg for pkg in table if pkg in merges]
    if not needed:
        log("cycle was broken by USE flags alone but no breaker package is part of "
            "the dependency graph; the table may need updating.")
        return 1

    log(f"emerging breaker packages: {' '.join(needed)}")
    emerge_cmd = ["emerge", "--oneshot", "--update", "--buildpkg", "--usepkg",
                  "--binpkg-respect-use=y"]
    if args.pretend:
        emerge_cmd.append("--pretend")
    emerge_cmd += emerge_opts + needed
    env = dict(os.environ, USE=use)
    subprocess.run(emerge_cmd, env=env, check=True)
    log("done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
