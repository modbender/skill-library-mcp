# Setup

## Prerequisites

- **Python 3.10+**
- **CUPS** printing system (macOS built-in, Linux: `apt install cups`)
- **Pillow** (only needed for image printing)

## Required System Tools

These are part of CUPS and should be pre-installed on macOS:

| Tool | Purpose |
|------|---------|
| `lp` | Submit print jobs |
| `lpstat` | List printers, check status |
| `lpoptions` | Query printer capabilities |

## Installation

```bash
# Verify setup
python3 {baseDir}/scripts/print.py list

# Install Pillow (only needed for image printing)
pip install Pillow
```

## Configuration

No configuration file needed. The skill uses:

- **System default printer** (set via System Settings or `lpoptions -d <printer>`)
- **PPD files** at `/etc/cups/ppd/<printer>.ppd` for paper sizes, margins, and resolution

Override the printer per-command with `--printer <name>`.

## Platform Notes

- **macOS**: CUPS is built-in. PPD files are at `/private/etc/cups/ppd/`.
- **Linux**: Install CUPS (`apt install cups`). PPD files are at `/etc/cups/ppd/`.
- **Windows**: Not supported (no CUPS).
