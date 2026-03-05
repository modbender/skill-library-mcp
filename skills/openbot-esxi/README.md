# ESXi Debian Deploy Skill

Zero-touch Debian 13 VM deployment on VMware ESXi 8 — built for [OpenClaw](https://github.com/openclaw/openclaw) AI agents.

## What it does

Deploys fully configured Debian 13 VMs on ESXi in ~8 minutes with zero manual interaction:

- **Custom preseed ISO** — automated Debian installer, no prompts
- **NVMe + vmxnet3** — modern, high-performance VM config
- **Serial console** — telnet access to VM console, even without network
- **Online disk resize** — grow disks without VM shutdown

## Quick Start

```bash
# Install as OpenClaw skill
openclaw skill install ./esxi-debian-deploy.skill

# Or use the deploy script directly
bash scripts/esxi-deploy.sh myvm 4 4096 50
```

## Requirements

- ESXi 8.x host with SSH access
- `govc` CLI, `xorriso`, `isolinux`, `sshpass`
- Debian/Ubuntu agent host

## Documentation

See [SKILL.md](SKILL.md) for full documentation including:
- Configuration options
- Serial console setup
- Disk resize usage
- Preseed customization
- Known gotchas

## Files

```
├── SKILL.md                          # Full skill documentation
├── scripts/
│   ├── esxi-deploy.sh                # Main deploy script
│   └── esxi-vm-resize-disk.sh        # Online disk resize
└── references/
    ├── preseed-template.cfg           # Preseed config template
    └── vmx-template.md               # VMX configuration reference
```

## License

See [LICENSE](LICENSE).
