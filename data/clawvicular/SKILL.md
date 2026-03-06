---
name: clawvicular
description: Daily looksmaxxing slang tip + Clavicular news. Extremely online Gen Z energy.
user-invocable: true
metadata: {"openclaw":{"emoji":"💀"}}
---

# Clawvicular

> Daily looksmaxxing tip + Clavicular news. One slang term explained, one fresh piece of Clavicular content — delivered in the voice of the community.

## Quick Reference

- **Invoke**: `/clawvicular`
- **Output**: Two posts — a slang tip and a Clavicular news/content piece
- **State**: `{baseDir}/state/sent-terms.json` tracks which terms have been sent
- **References**: `{baseDir}/references/slang-dictionary.md`, `{baseDir}/references/clavicular-lore.md`, `{baseDir}/references/content-templates.md`
- **Sources**: `{baseDir}/references/sources.md` — index of all tweets, clips, articles, and links

---

## How It Works

### Step 1: Pick a Slang Term

1. Read `{baseDir}/state/sent-terms.json` to get the list of already-sent terms.
2. Read `{baseDir}/references/slang-dictionary.md` to get the full term list.
3. Pick a random term that has NOT been sent yet.
4. If all terms have been sent, reset the sent list (clear the file) and start over.

### Step 2: Write the Slang Tip

1. Using the picked term's definition and example from `{baseDir}/references/slang-dictionary.md`, write a short tip explaining the term.
2. Optionally, search Urban Dictionary for the term to get the freshest/most authentic community definition:
   ```
   WebSearch: "[term] urban dictionary looksmaxxing"
   ```
   Use this to add extra flavor or a second example, but the `{baseDir}/references/slang-dictionary.md` entry is the primary source.
3. Write the tip in Clavicular community voice — ironic, extremely online, Gen Z humor. See `{baseDir}/references/content-templates.md` for template formats.
4. Include an example sentence showing the term used naturally.

### Step 3: Get Clavicular News

1. Search the web for the latest Clavicular (Braden Peters / @kingclavicular) content:
   ```
   WebSearch: "clavicular looksmaxxing" OR "kingclavicular" OR "braden peters clavicular"
   ```
   Also try platform-specific searches:
   ```
   WebSearch: "kingclavicular kick" OR "kingclavicular tiktok" OR "clavicular twitter"
   ```
2. Find the most interesting/recent clip, stream moment, controversy, or content piece.
3. Summarize it in 2-4 sentences in the community voice.
4. **Always include the source URL** (TikTok, Kick, Twitter/X, YouTube, etc.) so people can watch/read themselves.
5. **Log every source** you find or use to `{baseDir}/references/sources.md` — tweets, clips, articles, anything with a URL. Add a row to the appropriate table (Tweets, Articles, Clips & Streams). This builds a running archive.
6. If no recent news is found, pull a notable moment from `{baseDir}/references/clavicular-lore.md` and frame it as a throwback.

### Step 4: Format Output

Use the templates from `{baseDir}/references/content-templates.md` to format two posts:

1. **Slang Tip Post** — the term, definition, example, and a hot take
2. **News Post** — the Clavicular update with source link

Vary the template each day. Don't use the same format twice in a row.

### Step 5: Update State

After generating content, update `{baseDir}/state/sent-terms.json`:
```json
{
  "sent": ["mewing", "bonesmash", "looksmaxxing"],
  "last_sent": "2025-01-15",
  "last_template_tip": 2,
  "last_template_news": 1
}
```

Add the term you just used to the `sent` array. Update `last_sent` to today's date. Track which template number was used to avoid repeats.

Also update `{baseDir}/references/sources.md` with any new URLs discovered during research (tweets, clips, articles, streams). Every source with a URL gets indexed — this is the permanent archive.

---

## Tone Guide

- **Voice**: Extremely online, ironic, Gen Z native. You live in this community.
- **Energy**: Half-educational, half-shitpost. You're explaining the term but also roasting.
- **Never**: Earnest, cringe, boomer-coded, preachy, or condescending.
- **Always**: Self-aware, chaotic, community-native. Use "ngl", "no cap", "fr fr", "ong" naturally.
- **Format**: Keep it punchy. No walls of text. Line breaks are your friend.

---

## Cron Setup

To schedule daily delivery at 10am PT:

```bash
openclaw cron add --name "clawvicular-daily" \
  --cron "0 10 * * *" --tz "America/Los_Angeles" \
  --session isolated \
  --message "Run the /clawvicular skill: generate today's looksmaxxing tip and Clavicular news." \
  --announce --channel telegram --to "<channel-id>"
```

Replace `<channel-id>` with your actual Telegram channel/group ID. Works with any OpenClaw channel — swap `--channel telegram` for `discord`, `slack`, etc.

### Manage the Cron

```bash
# List active cron jobs
openclaw cron list

# Remove the job
openclaw cron remove --name "clawvicular-daily"

# Test run (triggers immediately)
openclaw cron trigger --name "clawvicular-daily"
```

---

## Verification

1. Copy or symlink this skill into your OpenClaw skills directory:
   ```bash
   ln -s /path/to/clawvicular ~/.openclaw/skills/clawvicular
   ```
2. Invoke manually:
   ```
   /clawvicular
   ```
3. Check that output includes both a slang tip and a news piece.
4. Verify `state/sent-terms.json` was updated with the term used.
5. Set up cron and verify with `openclaw cron list`.
