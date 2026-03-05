---
name: sonic-kvm-testbed
description: Deploy and manage a SONiC sonic-mgmt KVM virtual testbed with cEOS neighbors for running pytest-based network tests. Use when setting up a local KVM testbed, deploying T0/T1/T1-LAG topologies with converged cEOS peers, troubleshooting testbed-cli.sh or deploy-mg issues, tearing down and redeploying testbeds, or running sonic-mgmt test cases against a virtual SONiC switch (sonic-vs).
---

# SONiC KVM Virtual Testbed

Deploy a local sonic-mgmt KVM testbed with cEOS neighbors on a single machine.

## Architecture

```
Host Machine (KVM + Docker)
├── vlab-XX (KVM VM running sonic-vs) — DUT
├── ceos_vmsX-Y_VMZZ (Docker) — cEOS neighbor(s)
├── ptf_vmsX-Y (Docker) — PTF test traffic generator
└── sonic-mgmt (Docker) — Ansible + pytest framework
```

Management network: `br1` bridge, `10.250.0.0/24` (host at `.1`).

## Supported Topologies

| Testbed Name | Topo | DUT | VM Base | Neighbors (raw → converged) |
|---|---|---|---|---|
| `vms-kvm-t0` | t0 | vlab-01 | VM0100 | 4 → 1 cEOS |
| `vms-kvm-t1-lag` | t1-lag | vlab-03 | VM0104 | 24 → 2 cEOS |

Use `use_converged_peers: true` in vtestbed.yaml to reduce cEOS containers via multi-VRF convergence (requires PR #22399 in master branch).

## Prerequisites

- Ubuntu 20.04/22.04/24.04, KVM enabled (`kvm-ok`)
- 30GB+ RAM (for single topo) or 20GB+ with reduced VM memory
- Docker installed, user in `docker`, `kvm`, `libvirt` groups
- Built `sonic-vs.img.gz` from sonic-buildimage
- cEOS image file (e.g., `cEOS64-lab-4.32.5M.tar.xz`)
- `sshpass` installed on host

## Deploy Procedure

### 1. Initial Setup (one-time)

```bash
# Clone repo
git clone https://github.com/sonic-net/sonic-mgmt.git ~/sonic-mgmt
cd ~/sonic-mgmt && git checkout master  # PR #22399 needed for auto-convergence

# Prepare images
mkdir -p ~/veos-vm/images ~/sonic-vm/images
gunzip -k sonic-vs.img.gz
cp sonic-vs.img ~/veos-vm/images/ && cp sonic-vs.img ~/sonic-vm/images/

# Import cEOS (docker import, NOT docker load)
xz -d cEOS64-lab-4.32.5M.tar.xz
docker import cEOS64-lab-4.32.5M.tar ceosimage:4.32.5M

# Management bridge
cd ~/sonic-mgmt/ansible && sudo ./setup-management-network.sh

# debian:jessie dependency
docker pull publicmirror.azurecr.io/debian:jessie
docker tag publicmirror.azurecr.io/debian:jessie debian:jessie

# sonic-mgmt container
./setup-container.sh -n sonic-mgmt -d /data

# Create vault password file
echo "abc" > ~/sonic-mgmt/ansible/password.txt
```

### 2. Configure Credentials and Settings

See [references/credentials.md](references/credentials.md) for all config files.

**Critical files** (these reset on git operations — automate fixes in a script):

| File | Key Setting | Why |
|---|---|---|
| `group_vars/vm_host/creds.yml` | `vm_host_user: <your_user>` | Host SSH access |
| `group_vars/all/creds.yml` | `sonic_login: "<dut_user>"` | DUT SSH user (matches sonic-vs build user) |
| `group_vars/all/ceos.yml` | `skip_ceos_image_downloading: true` | Use local cEOS image |
| `group_vars/vm_host/main.yml` | `max_fp_num: 127` | Default 4 is too low for T0/T1 |
| `veos_vtb` | `ansible_user: <your_user>` | Inventory host user |
| `veos` | Comment out `STR-ACS-SERV-01` | Avoid dual-host conflict |
| `vars/docker_registry.yml` | Remove `:443` from host | `:443` causes docker pull to hang |
| `vtestbed.yaml` | `use_converged_peers: true` | Enable multi-VRF convergence |

**Create a fix script** to re-apply all settings. Run it before EVERY testbed operation.

### 3. Deploy Topology

```bash
# Fix configs + remove stale .bak
bash fix-configs.sh
rm -f vars/topo_<TOPO>.yml.bak

# Inside sonic-mgmt container:
./testbed-cli.sh -t vtestbed.yaml add-topo <TESTBED_NAME> password.txt
```

**Duration**: ~15-20 minutes (VM boot + cEOS startup).

### 4. Post-Deploy DUT Setup

After `add-topo`, the DUT boots with the build user. The `multi_passwd_ssh` plugin expects `admin`:

```bash
# SSH to DUT as build user
ssh <build_user>@<DUT_IP>

# Create admin user
sudo useradd -m -s /bin/bash -G sudo,docker admin
echo 'admin:password' | sudo chpasswd
sudo bash -c "echo 'admin ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/admin"

# Fix docker socket
sudo chmod 666 /var/run/docker.sock
```

### 5. Deploy Minigraph

```bash
# Fix configs + remove .bak AGAIN (they revert!)
bash fix-configs.sh
rm -f vars/topo_<TOPO>.yml.bak

./testbed-cli.sh -t vtestbed.yaml deploy-mg <TESTBED_NAME> veos_vtb password.txt
```

**Duration**: ~5-10 minutes.

### 6. Verify

```bash
# Check containers
docker ps | grep -E "ceos|ptf"

# Check BGP (use admin after deploy-mg)
sshpass -p password ssh admin@<DUT_IP> "show ip bgp summary"
```

**Expected BGP state with converged peers:**
- T0: ARISTA01T1 Established (6400 prefixes), ARISTA02-04T1 Active (normal — VRF peers without physical port-channels)
- T1-LAG: 17/24 sessions up (all T0 + 1 T2 spine; remaining T2 spines Active)

### 7. Run Tests

```bash
cd /data/sonic-mgmt/tests
./run_tests.sh -n <TESTBED_NAME> -d <DUT_NAME> -c <test_path> \
  -f vtestbed.yaml -i ../ansible/veos_vtb
```

## Teardown

```bash
bash fix-configs.sh
rm -f vars/topo_<TOPO>.yml.bak
./testbed-cli.sh -t vtestbed.yaml remove-topo <TESTBED_NAME> password.txt
```

**Duration**: ~12-15 minutes.

## Critical Gotchas

1. **Config files revert** during git and testbed operations — run fix script before EVERY command
2. **Remove `.bak` files** before `add-topo` — stale backups cause `KeyError` in converger
3. **`docker import`** for cEOS (not `docker load`)
4. **`:443` in docker_registry_host** silently hangs docker pulls
5. **`max_fp_num: 4`** is too low — set to 127
6. **`br1` bridge is not persistent** across reboots — add netplan config
7. **Non-admin builds**: sonic-vs uses the build machine's username, not `admin`
8. **`use_converged_peers: true`** requires master branch (PR #22399) for auto-convergence

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for detailed diagnosis of common failures.
