# Clawback Setup Reference

## Installation

```bash
pip install clawback
```

Or from source:

```bash
git clone https://github.com/yhyatt/clawback
cd clawback
pip install -e ".[dev]"
```

Verify:

```bash
clawback --help
```

## Google Sheets Integration (optional)

Clawback uses the `gog` CLI to write to Google Sheets. Without it, Clawback works in local-only mode.

```bash
npm install -g gog
gog auth login          # opens browser OAuth flow
gog auth status         # verify login
export GOG_KEYRING_PASSWORD=<your-password>   # add to shell profile
```

Add to `~/.zshrc` or `~/.bashrc`:
```bash
export GOG_KEYRING_PASSWORD=your-keyring-password
```

## First Trip Setup

```bash
# Create a trip (sets it as active for this chat)
clawback handle mygroup "kai trip Greece Vacation base EUR"
# → Confirm? 
clawback handle mygroup "yes"

# Add initial participants if needed (they're auto-added on first expense)
clawback handle mygroup "kai who"
```

## OpenClaw Integration

In your OpenClaw workspace, register the Clawback skill:

```bash
cp -r deploy/openclaw-skill ~/.openclaw/workspace/skills/clawback
```

Then in your `openclaw.json`, add clawback to the skills list, or it will be auto-discovered.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOG_KEYRING_PASSWORD` | If using Sheets | Password for gog keyring |
| `ANTHROPIC_API_KEY` | Only for oracle tests | Not needed for normal use |
| `CLAWBACK_DATA_DIR` | Optional | Override `~/.clawback/` data directory |

## State Directory

```
~/.clawback/
  trips.json     # All trips and their expenses/settlements
  pending.json   # Pending confirmations (5-min TTL)
  active.json    # chat_id → trip name mapping
```

Back this up if you care about the data. The Google Sheet is the authoritative shared view, but local state drives the logic.
