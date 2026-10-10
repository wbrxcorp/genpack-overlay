# genpack-overlay

This is the official Gentoo Portage overlay for the **genpack** toolchain, which is designed to build specialized, immutable OS images based on Gentoo Linux.

## Quick Map for Agents & Developers

- **`profiles/genpack/`**: Defines the profile hierarchy used to configure target system environments:
  - `base`: Common settings, kernel, init system, and base tools.
  - `systemimg`: Profile for baremetal deployments (BIOS/UEFI, drivers).
  - `paravirt`: Profile for virtualization (QEMU guest agents, virtio, vsock).
  - `gnome` / `weston`: UI/desktop environments.
- **`genpack/genpack/`**: The ebuild for the image builder itself. Installed *inside* artifact images to support self-building, development environments, and nested compilation.
- **`genpack/genpack-progs/`**: A critical utility package containing low-level helper tools (Python/Bash) for the build process (e.g., file copy-up, circular dependency resolution, and asset downloading).
  - *Agent Note*: This package inherits the `genpack-ignore` eclass. It is heavily utilized inside the build environment (Lower layer), but is **automatically excluded** from the final runtime image (Upper layer) to keep the OS footprint minimal.
- **`sys-apps/genpack-init/`**: The core startup provisioning module (C++ + Python/pybind11) acting as PID 1 to configure systems based on `system.ini`.
- **Other directories (`app-*`, `dev-*`, `net-*`, etc.)**: Custom ebuilds and utilities packaged specifically to serve as "components" inside `genpack` immutable artifacts.

## Documentation

For deep technical details about the architecture, build sequence, configuration format (JSON5), and component interactions, please refer to the documentation files in the core `genpack` repository:
- **Online**: [wbrxcorp/genpack](https://github.com/wbrxcorp/genpack)
- **Local**: Your local working copy of the core repository, under `docs/*.md` (particularly `introduction.md` and `cli.md`).

## Operational Guidelines

When adding or updating packages in this overlay:
1. Ensure they conform to Gentoo EAPI 8 standards.
2. Regenerate the package Manifest using `ebuild <file> manifest`.
3. Do not introduce circular dependencies unless mitigated through the package's USE flags.
4. For date-versioned ebuilds, if multiple updates are committed on the same day, append Gentoo-style revisions (e.g., -r1, -r2, etc.) rather than custom dash branches (e.g., use paravirt-20260614-r1.ebuild instead of custom dash versions).
5. Never commit Python compiled caches (`__pycache__` directories or `.pyc` files) inside any package's `files/` directory, as they break Portage digest verification. Always clean them before regenerating manifests.

## Testing ebuilds as an unprivileged user

`/var/tmp/portage` and `/var/cache/distfiles` are root-owned, and portage chowns its build directories to the `portage` user/group (gid 250), so a non-root user who is not a member of the `portage` group cannot run the build phases out of the box. Point portage at writable locations and at your own uid/gid for the duration of the test:

```sh
T=$(mktemp -d)
mkdir -p "$T/portage" "$T/git3-src"
export PORTAGE_TMPDIR="$T/portage"        # build area (default /var/tmp/portage is root-owned)
export PORTAGE_USERNAME="$USER"           # chown to self instead of the portage user
export PORTAGE_GRPNAME="$USER"
export EGIT3_STORE_DIR="$T/git3-src"      # git-r3 clone store (default under /var/cache/distfiles)

ebuild net-firewall/foo/foo-1.0.ebuild manifest   # works even without the env vars above
ebuild net-firewall/foo/foo-1.0.ebuild compile    # fetch + prepare + compile (sandboxed)
ebuild net-firewall/foo/foo-1.0.ebuild install    # populates the image dir only; nothing is merged
```

The installed tree is at `$PORTAGE_TMPDIR/portage/<category>/<PVP>/image` and can be inspected with `find`/`diff` after `install`.

Notes:
- `FEATURES="unprivileged"` does *not* help here: it raises portage's security pass to 2, which makes it chown to the portage group even more aggressively.
- To test a `git-r3` ebuild whose `EGIT_COMMIT` has not been pushed yet, work in a scratch overlay: point `EGIT_REPO_URI` at a local checkout (git accepts local paths), add `metadata/layout.conf` containing `masters = gentoo`, and regenerate the Manifest for the modified ebuild (`ebuild <file> manifest`), since the EBUILD digest changes.
- If a Makefile's default target performs installation (writes outside `$D`), portage's default `src_compile` (an implicit `emake`) will trip the sandbox; define an explicit no-op `src_compile()` in the ebuild and do the installation only in `src_install` with `DESTDIR="${D}"`.
