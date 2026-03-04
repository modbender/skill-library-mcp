# Clawvicular

An [OpenClaw](https://github.com/openclaw) skill that delivers daily looksmaxxing slang tips + Clavicular news.

## What's in here

- **SKILL.md** — The skill spec. Defines the workflow, tone, templates, and cron setup.
- **references/** — The knowledge base:
  - `slang-dictionary.md` — 300+ looksmaxxing terms with definitions and examples
  - `clavicular-lore.md` — Braden Peters biography, timeline, and key moments
  - `content-templates.md` — Tweet templates and tone guide
  - `sources.md` — Index of tweets, clips, articles, and memes
- **state/** — Tracks which terms have been posted

## Usage

### As an OpenClaw skill

```bash
# Symlink into your skills directory
ln -s /path/to/clawvicular ~/.openclaw/skills/clawvicular

# Invoke manually
/clawvicular

# Schedule daily at 10am PT
openclaw cron add --name "clawvicular-daily" \
  --cron "0 10 * * *" --tz "America/Los_Angeles" \
  --session isolated \
  --message "Run the /clawvicular skill: generate today's looksmaxxing tip and Clavicular news." \
  --announce --channel telegram --to "<channel-id>"
```

### As a reference

The `references/` directory is a standalone looksmaxxing knowledge base. Use it however you want — feed it to an LLM, build a bot, make a quiz, whatever.

## License

MIT
