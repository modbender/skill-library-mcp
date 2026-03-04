# Find My Skill for OpenClaw

Control Apple's Find My app via Peekaboo UI automation. Locate people, devices, and AirTags without third-party APIs or credential sharing.

## Why This Exists

Most Find My integrations require handing your Apple credentials to sketchy third-party services. This skill controls the native macOS app directly via UI automation - your data never leaves your machine.

## Requirements

- **macOS** (darwin only)
- **Find My.app** must be open
- **OpenClaw.app** with Peekaboo bridge (Screen Recording + Accessibility permissions)
- **peekaboo** CLI installed
- **jq** for JSON parsing

## Installation

Install via [ClawHub](https://clawhub.ai/loganprit/apple-find-my-local) or clone this repo into your skills directory.

## Privacy & Security

**What this skill accesses:**
- Location data for people, devices, and items in your Find My app
- Screenshots of the Find My window (stored locally in `/tmp/`)

**What this skill does NOT do:**
- No network requests to third-party services
- No credential storage or Apple ID access
- No data exfiltration - all operations are local UI automation

## Scripts

| Script | Purpose |
|--------|---------|
| `fm-window.sh` | Get window ID and bounds |
| `fm-screenshot.sh` | Capture Find My window |
| `fm-tab.sh` | Switch tabs (people/devices/items) |
| `fm-list.sh` | List items in a tab |
| `fm-select-item.sh` | Select item by position |
| `fm-locate.sh` | Show item location |
| `fm-info.sh` | Open info panel |
| `fm-play-sound.sh` | Play sound on AirTag |
| `fm-click.sh` | Click at coordinates |

## Known Limitations

1. `--app "Find My"` hangs in Peekaboo - uses `--window-id` workaround
2. Sidebar items not accessible via accessibility APIs - uses position-based selection
3. Cannot use computer while skill is running (mouse/click conflicts)

## License

MIT
