---
name: find-my
version: 1.0.1
description: Control Apple Find My app via Peekaboo to locate people, devices, and items (AirTags). Use when asked to find keys, wallet, AirTags, locate family members and friends, play sound on lost items, or check device locations. Native app control - no third-party APIs or credential sharing required.
metadata:
  os: [darwin]
  requires:
    bins: [peekaboo, jq]
    env:
      PEEKABOO_BRIDGE_SOCKET: "Path to OpenClaw.app Peekaboo bridge socket (default: ~/Library/Application Support/OpenClaw/bridge.sock)"
    env_optional:
      FM_OUTPUT_DIR: "Directory for screenshot output (default: /tmp)"
  contains_scripts: true
  privacy:
    screenshots: true
    location_data: true
    ui_automation: true
---

# Find My

Control the native Find My app via Peekaboo. No sketchy APIs or credential sharing.

**Run scripts from:** `cd {skillDir}`

## Requirements

| Requirement | Details |
|-------------|---------|
| **OS** | macOS only |
| **Apps** | Find My.app (must be open), OpenClaw.app (provides Peekaboo bridge) |
| **Permissions** | OpenClaw.app needs Screen Recording + Accessibility permissions |
| **Peekaboo** | CLI must be installed and configured |

## Privacy & Security

**What this skill accesses:**
- Location data for people, devices, and items in your Find My app
- Screenshots of the Find My window (stored locally in `/tmp/`)

**What this skill does NOT do:**
- No network requests to third-party services
- No credential storage or Apple ID access
- No data exfiltration — all operations are local UI automation

**Data scope:** The skill can see/interact with anything visible in your Find My app, including:
- Shared locations of family/friends
- Device locations (yours and Family Sharing members)
- AirTag/item locations

**User awareness:** This skill uses mouse clicks and UI automation. You will see the actions happening on screen.

## Known Limitations

1. **`--app "Find My"` hangs** in Peekaboo - use `--window-id` instead
2. **Sidebar items not accessible** - Find My doesn't expose item names via accessibility APIs
3. **Position-based selection** - Select items by position (1st, 2nd, 3rd...) not by name
4. **macOS only** - Requires Peekaboo + OpenClaw.app bridge
5. **Exclusive control** - User cannot interact with the Mac while skill is running (mouse/clicks conflict)

## Quick Reference

| Script | Purpose |
|--------|---------|
| `fm-window.sh` | Get window ID and bounds (JSON) |
| `fm-screenshot.sh [path]` | Capture Find My window |
| `fm-tab.sh <tab>` | Switch tab: `people`, `devices`, `items` |
| `fm-list.sh [tab]` | Screenshot + show sidebar positions |
| `fm-select-item.sh <pos> [tab]` | Select item by position (1, 2, 3...) |
| `fm-locate.sh <pos> [tab]` | Select item and screenshot location |
| `fm-info.sh [path]` | Open info panel, screenshot |
| `fm-play-sound.sh <pos>` | Attempt to play sound on item |
| `fm-click.sh <x> <y>` | Click at relative window coords |

## Workflow Examples

### List available items

```bash
./scripts/fm-list.sh items
# Screenshots the Items tab - view image to see your AirTags/items
```

### Find your keys (if keys are 2nd item in list)

```bash
./scripts/fm-locate.sh 2 items
# Shows location on map, outputs screenshot path
```

### Play sound on keys

```bash
./scripts/fm-play-sound.sh 2
# Selects 2nd item, attempts to click Play Sound
# May require manual click if button not found
```

### Check on a family member

```bash
./scripts/fm-list.sh people
# View screenshot to see who's listed

./scripts/fm-locate.sh 1 people
# Shows first person's location
```

## UI Layout Reference

### Tab Bar (y ≈ 68 from window top)
| Tab | X Position |
|-----|------------|
| People | ~63 |
| Devices | ~154 |
| Items | ~243 |

### Sidebar Items (x ≈ 150)
| Position | Y Coordinate |
|----------|--------------|
| 1st item | ~120 |
| 2nd item | ~174 |
| 3rd item | ~228 |
| 4th item | ~282 |
| (spacing) | +54px each |

## Manual Coordinate Clicks

When automation fails, calculate coordinates manually:

```bash
# Get window position
./scripts/fm-window.sh
# Output: {"x": 824, "y": 62, "width": 1024, "height": 768, "window_id": 2248}

# Click at relative position within window
./scripts/fm-click.sh 150 174   # 2nd sidebar item
./scripts/fm-click.sh 243 68    # Items tab
```

## Info Panel Actions

After selecting an item, click the ⓘ button on the map popup to open the info panel:

| Action | Description |
|--------|-------------|
| **Play Sound** | Make AirTag chirp (items only) |
| **Directions** | Open Maps with directions |
| **Share** | Share location with others |
| **Lost Mode** | Enable contact info sharing |
| **Notifications** | Configure alerts |

## Troubleshooting

**"Find My window not found"**
- Ensure Find My.app is open
- Check OpenClaw.app is running (provides Peekaboo bridge)

**Clicks not registering**
- Window may have moved - re-run `fm-window.sh` for fresh coordinates
- Ensure Find My is frontmost before clicking

**Can't find Play Sound button**
- Open info panel manually (click ⓘ on map popup)
- Then re-run play-sound script

## Future Improvements

When Peekaboo fixes `--app "Find My"`:
- Direct element targeting without coordinate calculation
- Reliable accessibility tree for sidebar items
- Simpler automation flows
