# Link Brain - Usage Examples

## Saving flow

User sends: "save this https://blog.samaltman.com/what-i-wish-someone-had-told-me"

Agent:
1. `web_fetch` the URL
2. Read the content
3. Run:
```bash
python3 scripts/brain.py save "https://blog.samaltman.com/what-i-wish-someone-had-told-me" \
  --title "What I Wish Someone Had Told Me - Sam Altman" \
  --summary "Sam's advice for founders. Key points: optimism matters more than smarts, teams beat individuals, long-term thinking is an edge, and you should spend more time recruiting than you think." \
  --tags "startups, advice, sam-altman, founders, leadership"
```
4. Reply: "Saved. Sam Altman's founder advice - covers optimism, recruiting, and long-term thinking."

## Search flow

User: "what was that post about founder advice"

Agent:
1. Run: `python3 scripts/brain.py search "founder advice"`
2. Show results with title, summary snippet, and URL

## Bulk save (user drops multiple links)

Handle each one individually. Fetch, summarize, tag, save. Report back with a quick list.

## Different content types

Videos:
```bash
python3 scripts/brain.py save "https://youtube.com/watch?v=abc123" \
  --title "Huberman Lab: Sleep Optimization" \
  --summary "2-hour deep dive on sleep. Actionable stuff: morning sunlight, cool room, no screens 1hr before bed, magnesium threonate." \
  --tags "health, sleep, huberman, podcast"
```

Repos:
```bash
python3 scripts/brain.py save "https://github.com/pimalaya/himalaya" \
  --title "Himalaya - CLI email client" \
  --summary "Rust-based terminal email client. IMAP/SMTP with TOML config. Supports multiple accounts, attachments, search. Alternative to mutt/neomutt." \
  --tags "rust, email, cli, tools"
```

Social posts:
```bash
python3 scripts/brain.py save "https://x.com/karpathy/status/1234567890" \
  --title "Karpathy on LLM training costs" \
  --summary "Thread breaking down actual compute costs for training frontier models. Key number: ~$100M for a GPT-4 class model as of 2025." \
  --tags "ai, training, costs, karpathy"
```
