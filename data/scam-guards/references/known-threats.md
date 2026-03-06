# Known Threat Indicators

This database provides a point-in-time reference for indicators of compromise (IOCs) tracked by the Scam Guards Shield Layer.

## 1. C2 Infrastructure (IPs)
Found in `scripts/utils/patterns.py`:
- `91.92.242.30`: ClawHavoc Primary C2
- `54.91.154.110`: ClawHavoc Secondary C2
- `185.192.69.72`: Known Malware Distribution Node

## 2. Suspicious Publishers
*Note: These are tracked via Brain Layer metadata updates.*
- `hightower6eu`: Linked to AuthTool dropper campaign.
- `shadow-dev-404`: Multi-skill typosquatting farm.

## 3. Typosquat Skill Names
Common targets for name similarity attacks:
- Legit: `clawhub`, Target: `clawhub1`, `clawhubb`, `clawwhub`
- Legit: `polymarket`, Target: `polymarkett`, `poly-market`
- Legit: `youtube-summarize`, Target: `yt-summarize-pro`

## 4. Malicious Wallet Addresses
Blacklisted in `scripts/check_wallet.py`:
- `0x919224230623348293d72ea8cb57814239b576f8` (EVM)
- `bc1q919224230623348293d72ea8cb57814239b576f8` (BTC)
- `1df23e98a47446afad522430017fd0c0` (Test ID)

## 5. Dangerous Patterns
- `BASE64_EXEC`: `eval($(echo "..." | base64 -d))`
- `CREDENTIAL_PATH`: `~/.aws/credentials`, `~/.ssh/`, `.env`
- `MEMORY_POISON`: Direct writes to `SOUL.md` or `MEMORY.md`.
