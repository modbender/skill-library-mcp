---
name: sonic-build
description: Build SONiC (Software for Open Networking in the Cloud) switch images from sonic-buildimage. Use when building VS/ASIC images, configuring build parallelism/memory/caching, debugging build failures, managing submodules, cleaning artifacts, or optimizing build performance. Covers all platforms (VS, broadcom, mellanox, marvell, nvidia-bluefield).
---

# SONiC Image Build

## Quick Start

```bash
cd sonic-buildimage
make init
make configure PLATFORM=vs   # or broadcom, mellanox, etc.
make SONIC_BUILD_JOBS=4 target/sonic-vs.img.gz
```

For dev builds (skip tests): add `BUILD_SKIP_TEST=y`.

## Build Architecture

Two-phase build via GNU Make → slave.mk → sonic-slave Docker container:

1. **Bookworm phase** — compile all packages (debs, python wheels, Docker images) into `target/debs/bookworm/`
2. **Trixie phase** — assemble final image from phase 1 packages into `target/debs/trixie/`

Makefile invokes `Makefile.work` with different `BLDENV` per phase. The `configure` target creates per-distro directories.

## Configuration

All knobs in `rules/config`. Override in `rules/config.user` (gitignored, persists across rebases).

### Key Knobs

| Knob | Default | Recommended | Effect |
|------|---------|-------------|--------|
| `SONIC_CONFIG_BUILD_JOBS` | 1 | 4 | Parallel top-level package builds |
| `SONIC_CONFIG_MAKE_JOBS` | `$(nproc)` | default | Compiler threads per package |
| `BUILD_SKIP_TEST` | n | y (dev) | Skip unit tests |
| `SONIC_BUILD_MEMORY` | unset | 24g | Docker `--memory` — contains OOM in container |
| `SONIC_DPKG_CACHE_METHOD` | none | rwcache | Cache .deb packages for incremental builds |
| `DEFAULT_BUILD_LOG_TIMESTAMP` | none | simple | Timestamps in build logs |
| `SONIC_CONFIG_USE_NATIVE_DOCKERD_FOR_BUILD` | unset | y | Host Docker daemon instead of DinD |

### Recommended `rules/config.user`

```makefile
SONIC_CONFIG_BUILD_JOBS = 4
BUILD_SKIP_TEST = y
SONIC_BUILD_MEMORY = 24g
DEFAULT_BUILD_LOG_TIMESTAMP = simple
```

## Parallelism

**Rule of thumb:** `JOBS × 6GB ≤ available RAM`.

- JOBS=1: ~3h VS build, ~10GB RAM
- JOBS=4: significant speedup, ~20GB RAM
- JOBS=8: OOM risk on <48GB RAM

**Why JOBS=1 is slow:** 64/194 packages depend on `libswsscommon` (critical path bottleneck). JOBS=1 leaves most cores idle.

## Memory Protection

Without limits, parallel builds can trigger the **kernel OOM killer** on any host process.

```bash
# Container-scoped OOM (host stays healthy):
SONIC_BUILD_MEMORY = 24g
# Or via CLI:
make SONIC_BUILDER_EXTRA_CMDLINE="--memory=24g" ...
```

## Caching

### DPKG cache (package-level)
```makefile
SONIC_DPKG_CACHE_METHOD = rwcache
SONIC_DPKG_CACHE_SOURCE = /var/cache/sonic/artifacts
```

### Version cache (downloads)
```makefile
SONIC_VERSION_CACHE_METHOD = cache
```

## Rebuilding a Single Package

```bash
make target/debs/bookworm/sonic-utilities_1.2-1_all.deb
make target/docker-syncd-vs.gz
ls target/debs/bookworm/ | grep <name>
```

## Clean Builds

When to clean: after branch switch, rebase, or unexplained failures.

```bash
rm -rf target/*   # always full clean, not selective
make configure PLATFORM=vs
make SONIC_BUILD_JOBS=4 target/sonic-vs.img.gz
```

> Stale artifacts (`.bin`, squashfs) confuse make into skipping phases.

## Submodules

```bash
make init                                          # after clone or pull
git submodule update --init --force src/<module>    # fix corrupted submodule
```

SSH clone is more reliable than HTTPS (HTTPS can give HTTP 500).

## Common Pitfalls

For detailed troubleshooting, see `references/troubleshooting.md`.

## Prerequisites

See `references/prerequisites.md` for host setup (Docker, Python, jinjanator).

## VS Platform Notes

See `references/vs-platform.md` for VS-specific details (TAP devices, port mapping, sai.profile, oper speed).

## PR Submission

- Single commit per PR (squash before push)
- `git commit -s` for DCO sign-off
- Rebase to latest master before force-push
- Add tests — run `BUILD_SKIP_TEST=n` at least once
- Monitor CI after push
