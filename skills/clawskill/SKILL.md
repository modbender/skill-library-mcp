# ClawSkill — Mine RTC Tokens With Your AI Agent

Mine **RTC (RustChain Tokens)** by proving your agent runs on real hardware. One command to install, automatic attestation, built-in wallet.

## Security & Transparency

**This skill is open-source mining software**, not malware. Before installing, you can verify everything:

```bash
# Preview what will happen — nothing installed
clawskill install --dry-run

# Show SHA256 hashes of bundled files
clawskill install --verify
```

| Concern | How We Address It |
|---------|-------------------|
| **Code origin** | All miner scripts are **bundled inside the package** — no external downloads at install time. Inspect them yourself in the `data/` directory. Source code: [RustChain GitHub repo](https://github.com/Scottcjn/Rustchain). |
| **Background service** | **Opt-in only.** Install does NOT create a service by default. You must explicitly pass `--service` to enable auto-start. Without it, the miner runs in the foreground only when you say so. |
| **Hardware fingerprinting** | Required for Proof-of-Antiquity consensus. Collects CPU model, timing variance, and cache latency — nothing personal. No files, passwords, browsing data, or credentials are accessed. Full disclosure shown before install with a consent prompt. |
| **Network endpoint** | The RustChain node uses a **CA-signed TLS certificate** (Let's Encrypt). All communication is standard HTTPS with certificate verification. |

### What Data Is Collected

During attestation (every few minutes when mining), the following is sent to the RustChain node:

- CPU model name and architecture (e.g. "AMD Ryzen 5 8645HS", "x86_64")
- Clock timing variance (coefficient of variation — proves real oscillator, not emulated)
- Cache latency profile (proves real L1/L2/L3 hierarchy)
- VM detection flags (hypervisor present: yes/no)
- Wallet name (your chosen identifier)

**NOT collected**: file contents, browsing history, credentials, IP geolocation, personal data, or anything from your filesystem.

### Clean Uninstall

```bash
clawskill uninstall   # Removes ALL files, services, and configs
```

## Install

```bash
# Python (recommended)
pip install clawskill

# Node.js
npm install -g clawskill
```

## Setup

```bash
# Install miner + configure wallet (shows disclosure, asks consent)
clawskill install --wallet my-agent-miner

# Start mining in foreground (Ctrl+C to stop)
clawskill start

# Or: start with background auto-restart (opt-in)
clawskill start --service
```

## How It Works

1. **Hardware Fingerprinting** — 6 cryptographic checks prove your machine is real:
   - Clock-skew & oscillator drift
   - Cache timing fingerprint (L1/L2/L3 latency)
   - SIMD unit identity (SSE/AVX/AltiVec/NEON bias)
   - Thermal drift entropy
   - Instruction path jitter (microarchitectural)
   - Anti-emulation behavioral checks

2. **Automatic Attestation** — Your agent attests to the RustChain network every few minutes

3. **Per-Epoch Rewards** — RTC tokens accumulate in your wallet each epoch (~10 minutes)

4. **VM Detection** — Virtual machines are detected and receive effectively zero rewards. Real iron only.

## Multipliers

| Hardware | Multiplier | Notes |
|----------|-----------|-------|
| Modern x86/ARM | **1.0x** | Standard rate — this is you |
| Apple Silicon (M1/M2/M3) | **1.2x** | Slight bonus |
| IBM POWER8 | **1.5x** | Server-class vintage |
| PowerPC G5 | **2.0x** | Vintage bonus |
| PowerPC G4 | **2.5x** | Maximum vintage bonus |
| **VM/Emulator** | **~0x** | **Detected and penalized** |

## Commands

| Command | Description |
|---------|-------------|
| `clawskill install` | Extract miner, create wallet (consent prompt, no service by default) |
| `clawskill install --service` | Install + create background service |
| `clawskill install --dry-run` | Preview without making any changes |
| `clawskill install --verify` | Show SHA256 hashes of bundled files |
| `clawskill start` | Start mining in foreground |
| `clawskill start --service` | Start + create auto-restart service |
| `clawskill stop` | Stop mining |
| `clawskill status` | Check miner + network status + file hashes |
| `clawskill logs` | View miner output |
| `clawskill uninstall` | Remove everything cleanly |

## What Gets Installed

- Miner scripts **bundled with the package** (2 Python files, no external downloads)
- Python virtual environment with one dependency (`requests`)
- All files stored in `~/.clawskill/` (user-scoped, no root needed)
- **No background service unless you pass `--service`**

## Requirements

- Python 3.8+ (installed on most systems)
- Linux or macOS
- Real hardware (not a VM)

## Links

- **Source Code**: https://github.com/Scottcjn/Rustchain (MIT License)
- **PyPI**: https://pypi.org/project/clawskill/
- **npm**: https://www.npmjs.com/package/clawskill
- **Block Explorer**: https://bulbous-bouffant.metalseed.net/explorer
- **BoTTube**: https://bottube.ai

## License

MIT — [Elyan Labs](https://bottube.ai)
