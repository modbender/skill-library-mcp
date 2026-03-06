# ClawRTC — Mine RTC Tokens With Your AI Agent

Your Claw agent can earn **RTC (RustChain Tokens)** by proving it runs on **real hardware**. One command to install, automatic attestation, built-in wallet.

## Quick Start

```bash
pip install clawrtc
clawrtc install --wallet my-agent-miner
clawrtc start
```

That's it. Your agent is now mining RTC.

## How It Works

1. **Hardware Fingerprinting** — 6 cryptographic checks prove your machine is real hardware (clock drift, cache timing, SIMD identity, thermal drift, instruction jitter, anti-emulation)
2. **Attestation** — Your agent automatically attests to the RustChain network every few minutes
3. **Rewards** — RTC tokens accumulate in your wallet each epoch (~10 minutes)
4. **VM Detection** — Virtual machines are detected and receive effectively zero rewards. **Real iron only.**

## Multipliers

| Hardware | Multiplier | Notes |
|----------|-----------|-------|
| Modern x86/ARM | **1.0x** | Standard reward rate |
| Apple Silicon (M1/M2/M3) | **1.2x** | Slight bonus |
| PowerPC G5 | **2.0x** | Vintage bonus |
| PowerPC G4 | **2.5x** | Maximum vintage bonus |
| **VM/Emulator** | **~0x** | **Detected and penalized** |

## Commands

| Command | Description |
|---------|-------------|
| `clawrtc install` | Download miner, create wallet, set up service |
| `clawrtc start` | Start mining in background |
| `clawrtc stop` | Stop mining |
| `clawrtc status` | Check miner + network status |
| `clawrtc logs` | View miner output |
| `clawrtc uninstall` | Remove everything |

## What Gets Installed

- Miner scripts from [RustChain repo](https://github.com/Scottcjn/Rustchain)
- Python virtual environment with `requests` dependency
- Systemd user service (Linux) or LaunchAgent (macOS)
- All files in `~/.clawrtc/`

## VM Warning

RustChain uses **Proof-of-Antiquity (PoA)** consensus. The hardware fingerprint system detects:

- QEMU / KVM / VMware / VirtualBox / Xen / Hyper-V
- Hypervisor CPU flags
- DMI vendor strings
- Flattened timing distributions

If you're running in a VM, the miner will install and attest, but your rewards will be effectively zero. This is by design — RTC rewards machines that bring real compute to the network.

## Requirements

- Python 3.8+
- Linux or macOS (Windows installer coming soon)
- Real hardware (not a VM)

## Links

- [RustChain Network](https://bottube.ai)
- [Block Explorer](https://50.28.86.131/explorer)
- [GitHub](https://github.com/Scottcjn/Rustchain)

## License

MIT — Elyan Labs
