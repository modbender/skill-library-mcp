# hme — Hide My Email CLI

Generate Apple **Hide My Email** addresses from the terminal.

No private APIs. No cookies. No browser. Just AppleScript driving System Settings.

![hme demo](hme.gif)

```bash
$ hme "Netflix"
✓ cob************@icloud.com (copied to clipboard)
```

## Install

Clone the repo and run the installer:

```bash
git clone --depth=1 https://github.com/manikal/hide-my-email.git ~/.hme
~/.hme/install.sh
```

Or if you prefer a one-liner (inspect [install.sh](install.sh) first):

```bash
curl -fsSL https://raw.githubusercontent.com/manikal/hide-my-email/v1.0.1/install.sh | sh
```

Installs to `~/.hme/bin/`. No sudo required. The installer prints a command to add it to your PATH.

Then grant Accessibility permissions to Terminal:
**System Settings → Privacy & Security → Accessibility → add Terminal**

## Usage

```bash
hme "Twitter"
hme "Shopping" "For online orders"
hme --help
```

The generated address is printed to stdout and copied to your clipboard.

## Requirements

- macOS Tahoe (26.x)
- iCloud+ subscription
- Terminal with Accessibility permissions

## How it works

Automates the same flow you'd do manually:

1. Opens System Settings → iCloud
2. Clicks Hide My Email → Create New Address
3. Reads the generated address
4. Fills in your label (and optional note)
5. Clicks Continue
6. Copies the address to clipboard

## Limitations

- **~10 second runtime** — UI automation needs time for elements to load
- **Rate limited by Apple** — roughly 5 addresses per 30 minutes
- **Screen access required** — not suitable for headless/SSH sessions
- **Window is repositioned** — the script moves System Settings to a fixed position for reliable element targeting

## Caveat

This tool works by scripting the System Settings UI. Apple can change the UI at any time and break it. It's a scratch-your-own-itch open source project — not production software. Pull requests welcome when it breaks.

## Troubleshooting

| Problem | Solution |
|---|---|
| `"Can't get sheet 1..."` | Increase `delay` values in the AppleScript — your Mac may be slower |
| `"Timed out waiting..."` | Make sure you're signed into iCloud with an active iCloud+ subscription |
| `"Not allowed assistive access"` | Grant Accessibility permissions to Terminal (see above) |

## License

MIT
