---
name: imessage-signal-analyzer
description: Analyze iMessage (macOS) and Signal conversation history to reveal relationship dynamics — message volume, initiation patterns, silence gaps, tone samples, and recent exchanges. Use when asked to analyze messages, read message history, check conversation patterns, or evaluate a relationship based on text history. Works on macOS (iMessage + Signal), Linux/Windows (Signal only).
---

# iMessage & Signal Analyzer

Analyze iMessage (macOS) and Signal conversations to produce relationship reports.

## Prerequisites

### macOS (iMessage)
iMessage data is stored locally on macOS. Depending on your security settings, you may need to grant Full Disk Access:

**Option 1:** Run the script directly with Python (no special permissions needed if you have read access to `~/Library/Messages/chat.db`)

**Option 2:** If you get a permission error, grant Full Disk Access:
- Open **System Settings → Privacy & Security → Full Disk Access**
- Click **+** and add Python or your terminal app

### Linux / Windows (Signal only)
- iMessage is not available on Linux/Windows
- Signal analysis works via exported JSON

### Signal (All Platforms)
- Install signal-cli: `brew install signal-cli` (macOS) or see https://github.com/AsamK/signal-cli
- Link your device: `signal-cli link` and scan QR code
- Export messages: `signal-cli export --output ~/signal_export.json`

## Usage

### iMessage Analysis
```bash
python3 skills/message-analyzer/scripts/analyze.py imessage <phone_or_handle>
```

**Examples:**
```bash
python3 skills/message-analyzer/scripts/analyze.py imessage "+15551234567"
python3 skills/message-analyzer/scripts/analyze.py imessage "+15551234567" --limit 500
```

### Signal Analysis
First, export your Signal data (one-time):
```bash
signal-cli export --output ~/signal_export.json
```

Then analyze:
```bash
python3 skills/message-analyzer/scripts/analyze.py signal ~/signal_export.json <phone_or_name>
```

**Examples:**
```bash
python3 skills/message-analyzer/scripts/analyze.py signal ~/signal_export.json "+15551234567"
python3 skills/message-analyzer/scripts/analyze.py signal ~/signal_export.json "+15559876543"
```

## Finding a Contact's Number

### iMessage
If you have a name but not a number:
```bash
DB=$(ls ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb 2>/dev/null | head -1)
sqlite3 "$DB" "SELECT ZFIRSTNAME, ZLASTNAME FROM ZABCDRECORD WHERE ZFIRSTNAME LIKE '%Name%';"
```
If AddressBook returns no results, ask the user for the number.

### Signal
Signal exports include phone numbers in the JSON. Search by name or number.

## Key Data Caveats

### iMessage
- **Your sent messages** may only exist from the current device's setup date — older sent messages are lost when switching devices. This skews initiation stats.
- **Binary messages** (attributedBody) are partially decoded — some formatting artifacts like `+@` prefixes may appear in samples; these are normal.
- **Multiple handles**: One contact may have 2–3 duplicate handles (iMessage + SMS + RCS). The script aggregates them automatically.

### Signal
- **Export required**: You must export Signal data first using `signal-cli export`
- **Media**: Exported JSON contains message text; media (images, files) is not included
- **Reactions**: Emoji reactions are included as separate message entries

## Analysis Output

The script produces:
- Total message count (you vs. them)
- Date range
- Messages per year with volume bar
- Conversation initiation breakdown (new convo = gap > 4 hours)
- Notable silences (>30 days)
- Sample messages by year
- Most recent 10 messages

## Interpreting Results

After running the script, synthesize findings conversationally:
- **Volume patterns**: When was the friendship most active? Any notable surges or drops?
- **Initiation skew**: Who reaches out first? (Note: your sent messages may be missing from old periods)
- **Gaps**: Were long silences mutual drift or explainable (device switch, platform change, life event)?
- **Tone/content**: What do the sample messages reveal about the relationship's energy?
- **Context from user**: Always ask the user to fill in context gaps

Present the analysis conversationally, not just as raw numbers. Offer a genuine take on the relationship dynamic.
