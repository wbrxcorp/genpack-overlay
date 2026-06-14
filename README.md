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
