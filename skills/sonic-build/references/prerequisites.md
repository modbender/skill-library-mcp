# Prerequisites

## Hardware

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 16+ cores |
| RAM | 8 GB | 32 GB+ |
| Disk | 300 GB free | 500 GB+ |
| KVM | Required | Required (nested virt for VMs) |

## Host OS

Ubuntu 22.04 or 24.04 recommended.

## Python & Jinja

```bash
sudo apt install -y python3-pip
pip3 install --user jinjanator
```

> `j2cli` is broken on Python 3.12+ (uses removed `imp` module). Use `jinjanator` — drop-in replacement.

Ensure `~/.local/bin` is in `$PATH` (re-login after install).

## Docker

```bash
sudo apt install -y docker-ce docker-ce-cli
sudo gpasswd -a ${USER} docker
newgrp docker  # or re-login
sudo modprobe overlay
```

Linux kernel 5.3+ requires Docker 20.10.10+ (clone3 syscall).

Remove any snap-based Docker installation first to avoid read-only filesystem bugs.

## Automated Setup

A local copy of the upstream prerequisites script is bundled at `scripts/prerequisites.sh` (relative to this skill's root).

```bash
# Run the bundled script (no network fetch needed):
bash <skill_dir>/scripts/prerequisites.sh

# Override defaults via env vars:
SONIC_REPO=git@github.com:sonic-net/sonic-buildimage.git \
SONIC_DIR=~/sonic-buildimage \
BRANCH=master \
  bash <skill_dir>/scripts/prerequisites.sh
```

Installs pip, jinjanator, Docker, configures groups, and clones the repo with submodules.

> The script is sourced from `sonic-buildimage/scripts/prerequisites.sh`. To update, copy the latest version from the repo.
