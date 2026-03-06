# 📊 Gumroad Analytics Skill

Pull product and sales data from Gumroad's API for tracking, analysis, and correlation with marketing efforts.

## Features

- **Quick stats** — See all products and top performers
- **Daily logging** — Automatic metrics snapshots for trend analysis
- **Sales export** — Filter by date or product
- **No jq dependency** — Works with basic shell tools

## Setup

1. Get your Gumroad API token:
   - Go to Gumroad → Settings → Advanced → Applications
   - Create an application and copy the access token

2. Save credentials:
```bash
mkdir -p ~/.config/gumroad
cat > ~/.config/gumroad/credentials.json << EOF
{
  "access_token": "YOUR_TOKEN_HERE"
}
EOF
chmod 600 ~/.config/gumroad/credentials.json
```

3. Install the skill:
```bash
clawdhub install gumroad
```

## Usage

### Quick Stats
```bash
./scripts/gumroad-stats.sh
```

### Daily Metrics (for cron)
```bash
./scripts/gumroad-daily.sh
```
Logs to `memory/metrics/gumroad/YYYY-MM-DD.json`

### Export Sales
```bash
./scripts/gumroad-sales.sh --after 2026-02-01
./scripts/gumroad-sales.sh --json > sales.json
```

## Metrics Format

Daily snapshots include:
- Product counts (total/published)
- Recent sales (30-day window)
- Day-over-day comparison

## Use Cases

- **Morning dashboard** — Include in heartbeat for daily revenue check
- **Marketing correlation** — Track if Moltbook posts drive sales
- **Conversion analysis** — Identify which products convert best
- **Trend detection** — Alert on sales spikes or drops

## API Reference

See `SKILL.md` for full endpoint documentation.

## License

MIT
