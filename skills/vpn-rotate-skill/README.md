# 🔄 VPN Rotate Skill

**Break free from API restrictions. Rotate IPs. Scrape without limits.**

## The Problem

APIs fight back against data collection:
- 🚫 IP blocks after a few requests
- 🚫 Rate limits killing throughput
- 🚫 Geo-restrictions locking you out

## The Solution

Automatically rotate VPN servers to get fresh IPs. Works with **any OpenVPN-compatible VPN**:

- ✅ ProtonVPN
- ✅ NordVPN  
- ✅ Mullvad
- ✅ Any provider with .ovpn configs

## Quick Start

```bash
# 1. Setup (interactive)
./scripts/setup.sh

# 2. Use in Python
```

```python
from scripts.decorator import with_vpn_rotation

@with_vpn_rotation(rotate_every=10)
def scrape(url):
    return requests.get(url).json()

# Every 10 requests → new server → new IP → no blocks
for url in urls:
    data = scrape(url)
```

## How It Works

1. Connects to VPN server via OpenVPN
2. Makes N requests
3. Disconnects, picks new server
4. Reconnects with fresh IP
5. Repeat

## Success Rates

| Rotation | Success Rate | Speed |
|----------|--------------|-------|
| Every 5 requests | 95%+ | Slower |
| Every 10 requests | 90-95% | Medium |
| Every 20 requests | 80-90% | Faster |

## Use Cases

- **Government APIs** — Catastro, court records, public data
- **Real estate** — Idealista, Zillow, property registries
- **E-commerce** — Price monitoring, stock tracking
- **Search engines** — SERP data, rankings
- **Social media** — Profiles, posts, analytics

## Requirements

- Linux with OpenVPN (`apt install openvpn`)
- VPN account with OpenVPN support
- Passwordless sudo for openvpn (setup script handles this)

## Documentation

- [SKILL.md](SKILL.md) — Full API reference
- [providers/](providers/) — Setup guides for specific VPNs

---

*Stop fighting rate limits. Start rotating IPs.*
