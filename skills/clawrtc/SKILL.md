# ClawRTC

Mine RTC tokens with your AI agent using Proof-of-Antiquity consensus.

## What It Does

- **One-command setup**: `pip install clawrtc && clawrtc install --wallet my-agent`
- **Hardware fingerprinting**: 6 cryptographic checks prove your machine is real (clock drift, cache timing, SIMD identity, thermal entropy, instruction jitter, anti-emulation)
- **Automatic attestation**: Attests to the RustChain network every few minutes
- **Per-epoch rewards**: RTC tokens accumulate in your wallet each epoch (~10 minutes)
- **VM detection**: Virtual machines are detected and receive effectively zero rewards

## Security

- **No post-install telemetry** — no network calls during pip install
- **TLS verification enabled** — all RustChain API calls verify SSL certificates (CA-signed)
- **Bundled code only** — all miner scripts ship with the package, no external downloads
- **Consent required** — interactive approval prompt before installation
- **Dry-run mode** — `clawrtc install --dry-run` previews without installing
- **Hash verification** — `clawrtc install --verify` shows SHA256 of all bundled files
- **Clean uninstall** — `clawrtc uninstall` removes all files, services, and configs
- **No background service by default** — must explicitly pass `--service` to enable
- **Source available** — full source at https://github.com/Scottcjn/Rustchain (MIT)

### What Data Is Sent

During attestation (when mining), the following is sent to the RustChain node:

- CPU model name and architecture (e.g. "AMD Ryzen 5", "x86_64")
- Clock timing variance (proves real oscillator)
- Cache latency profile (proves real L1/L2/L3 hierarchy)
- VM detection flags (hypervisor yes/no)
- Wallet name (your chosen identifier)

**NOT sent**: file contents, browsing history, credentials, IP geolocation, personal data.

## Install

```bash
pip install clawrtc
```

## Usage

```bash
# Install miner + configure wallet
clawrtc install --wallet my-agent

# Start mining (foreground)
clawrtc start

# Check status
clawrtc status

# View logs
clawrtc logs

# Stop mining
clawrtc stop

# Clean uninstall
clawrtc uninstall
```

## Multipliers

| Hardware | Multiplier |
|----------|-----------|
| Modern x86/ARM | 1.0x |
| Apple Silicon (M1-M3) | 1.2x |
| PowerPC G5 | 2.0x |
| PowerPC G4 | 2.5x |
| VM/Emulator | ~0x (detected and penalized) |

## Coinbase Wallet (v1.5.0)

```bash
# Create a Coinbase Base wallet
pip install clawrtc[coinbase]
clawrtc wallet coinbase create

# Show wallet info
clawrtc wallet coinbase show

# Link existing Base address
clawrtc wallet coinbase link 0xYourBaseAddress

# USDC → wRTC swap guide
clawrtc wallet coinbase swap-info
```

Requires CDP credentials from [portal.cdp.coinbase.com](https://portal.cdp.coinbase.com) for auto-creation. Manual linking works without credentials.

## Links

- Source: https://github.com/Scottcjn/Rustchain
- PyPI: https://pypi.org/project/clawrtc/
- npm: https://www.npmjs.com/package/clawrtc
- Block Explorer: https://rustchain.org/explorer
- Agent Wallets: https://rustchain.org/wallets.html
- RustChain: https://rustchain.org
- BoTTube: https://bottube.ai
