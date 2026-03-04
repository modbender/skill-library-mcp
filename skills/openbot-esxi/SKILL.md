---
name: esxi-debian-deploy
description: Zero-touch Debian 13 VM deployment on VMware ESXi 8. Builds custom preseed ISO, creates NVMe+vmxnet3 VM with serial console, and runs unattended installation. Use when deploying Debian VMs on ESXi, automating VM provisioning, or setting up serial console access for headless ESXi VM management.
---

# ESXi Debian 13 Zero-Touch Deploy

Deploy fully configured Debian 13 VMs on ESXi 8 in ~8 minutes with zero manual interaction.

## Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ESXI_HOST` | **Yes** | ESXi host IP address |
| `ESXI_PASS` | **Yes** | ESXi root password |
| `ESXI_USER` | No | ESXi user (default: `root`) |
| `ESXI_DATASTORE` | No | Target datastore (default: `datastore1`) |
| `NETWORK` | No | Port group name (default: `VM Network`) |
| `DOMAIN` | No | Domain for VMs (default: `local`) |
| `VM_PASS` | **Yes** (resize only) | VM root password for disk resize script |

> **⚠️ Note:** The deploy script generates a random VM password and prints it to stdout. The password is also embedded in the preseed ISO uploaded to the ESXi datastore. Remove the ISO after deployment and treat stdout output as sensitive.

## Requirements

- **ESXi 8.x** host with SSH and datastore access
- **govc** CLI ([github.com/vmware/govmomi](https://github.com/vmware/govmomi))
- **xorriso**, **isolinux** — for custom ISO build
- **sshpass** — for automated SSH/SCP
- Tools on agent host: `bash`, `python3`, `wget`

Install on Debian/Ubuntu:
```bash
apt install xorriso isolinux sshpass
# govc: https://github.com/vmware/govmomi/releases
```

## Usage

All credentials are passed via environment variables — nothing is hardcoded or embedded in process arguments.

```bash
export ESXI_HOST="192.168.1.100"
export ESXI_PASS="your-esxi-root-password"

bash scripts/esxi-deploy.sh [hostname] [cpu] [ram_mb] [disk_gb] [serial_port]
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| hostname | random animal name | VM name |
| cpu | 2 | vCPU count |
| ram_mb | 2048 | Memory in MB |
| disk_gb | 20 | Disk size in GB |
| serial_port | random 8600-8699 | Telnet port for serial console |

**Example:**
```bash
bash scripts/esxi-deploy.sh webserver 4 4096 50 8610
```

## What It Does

1. **Generate preseed.cfg** — German locale, DHCP, configurable user + `root`, random password
2. **Build custom ISO** — Debian netinst + preseed, patched isolinux for auto-boot
3. **Upload ISO** to ESXi datastore
4. **Create VM** — NVMe disk (thin provisioned), dual NIC (E1000 for installer + vmxnet3 for production), serial port via telnet
5. **Boot + unattended install** — preseed handles everything
6. **Post-install** — Remove E1000, eject ISO, set boot to HDD
7. **Output credentials** — SSH + serial console access details

## Serial Console

Every VM gets a serial port accessible via telnet to the ESXi host:

```bash
telnet <ESXI_IP> <serial_port>
```

Works even when the VM has no network. Configured:
- GRUB: `GRUB_TERMINAL="console serial"`, serial 115200 8N1
- Kernel: `console=tty0 console=ttyS0,115200n8`
- Getty: `serial-getty@ttyS0.service` enabled

**ESXi firewall requirement** (activated automatically by the script):
```bash
esxcli network firewall ruleset set -e true -r remoteSerialPort
```

**Important:** Set serial port IP to the ESXi host IP, not `0.0.0.0`:
```
serial0.fileName = "telnet://<ESXI_IP>:<port>"
```

## Online Disk Resize

Grow a VM's disk without shutdown:

```bash
export ESXI_HOST="192.168.1.100"
export ESXI_PASS="your-esxi-password"
export VM_PASS="vm-root-password"

bash scripts/esxi-vm-resize-disk.sh <vm-name> <new-size-gb>
```

Requires `cloud-guest-utils` on the VM (pre-installed by the deploy script).

## Configuration

All settings are configurable via environment variables:

```bash
export ESXI_HOST="192.168.1.100"    # ESXi host IP (required)
export ESXI_PASS="secret"           # ESXi root password (required)
export ESXI_USER="root"             # ESXi user (default: root)
export ESXI_DATASTORE="datastore1"  # Target datastore (default: datastore1)
export NETWORK="VM Network"         # Port group name (default: VM Network)
export DOMAIN="example.local"       # Domain for VMs (default: local)
```

No credential store or external resolver is required. Pass secrets via environment variables only — they are never embedded in process arguments or URLs.

## VM Configuration Details

| Component | Choice | Reason |
|-----------|--------|--------|
| Disk controller | NVMe | Faster than SCSI/SATA for modern guests |
| Production NIC | vmxnet3 | Paravirtualized, best performance |
| Installer NIC | E1000 | Kernel driver built-in, no firmware needed |
| Boot mode | BIOS | Simpler for automated installs |
| Provisioning | Thin | Saves datastore space |

## Preseed Highlights

- Locale: `de_DE.UTF-8`, keyboard `de`, timezone `Europe/Berlin`
- Partitioning: automatic, single root + swap
- Packages: `open-vm-tools`, `curl`, `sudo`, `qemu-guest-agent`, `cloud-guest-utils`
- SSH: `PermitRootLogin yes`, `PasswordAuthentication yes`
- Blacklisted modules: `floppy`, `pcspkr` (prevent I/O error loops in VMs)

Customize the preseed section in `esxi-deploy.sh` for different locales or packages.

## Security Considerations

- **Credentials**: All secrets are passed via environment variables, never embedded in URLs or process arguments. `govc` uses `GOVC_USERNAME`/`GOVC_PASSWORD` env vars.
- **SSH access**: The script uses `sshpass` for automated SSH. For production, consider SSH key-based auth instead.
- **Serial console**: Telnet is unencrypted. The serial port is bound to the ESXi host IP (not `0.0.0.0`), but anyone with network access to the ESXi host can connect. Restrict access via:
  - ESXi firewall rules (limit `remoteSerialPort` to trusted IPs)
  - Network segmentation / VPN
  - Disable serial port after debugging
- **Generated passwords**: VM passwords are output to stdout. Redirect output or use a credential store in production.
- **Lab use recommended**: Test on a lab ESXi host before using in production. Review all scripts before running.

## Gotchas

- **No heredoc in preseed `late_command`** — Shell expansion in the deploy script's heredoc destroys nested heredocs. Use `echo -e` or single-line commands instead.
- **Serial console only works after install** — The Debian installer uses VGA; serial output starts at first boot (GRUB + kernel).
- **ESXi firewall blocks serial by default** — The `remoteSerialPort` ruleset must be enabled.
- **Don't resize MBR partitions live** with extended/swap layout — Use `growpart` on the root partition or redeploy with larger disk.
- **E1000 removal requires shutdown** — The script handles this automatically post-install.

## References

- [references/preseed-template.cfg](references/preseed-template.cfg) — Full preseed config template
- [references/vmx-template.md](references/vmx-template.md) — VMX configuration reference
