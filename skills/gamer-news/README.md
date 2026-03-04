# gamer-news-skill

> ClawHub skill — Fetches and summarizes the latest video game news from major gaming outlets

## Install

```bash
npx clawhub@latest install gamer-news
```

## Sources

| Outlet | Focus |
|--------|-------|
| IGN | Broad coverage |
| Kotaku | News & culture |
| GameSpot | Reviews & news |
| Polygon | Features & culture |
| Eurogamer | EU perspective + tech analysis |
| Rock Paper Shotgun | PC gaming |
| VG247 | Breaking news |
| Gematsu | Japanese / Asian games |
| PlayStation Blog | Official Sony announcements |

## Usage

| Trigger | Example |
|---------|---------|
| Slash command | `/gamer-news` |
| Korean keyword | `요즘 게임 뉴스 뭐 있어?` |
| English keyword | `What's new in gaming today?` |
| Platform-specific | `PS5 최신 소식` / `PC game news` |

## What it does

1. Fetches RSS feeds from up to 9 major gaming outlets simultaneously
2. Deduplicates stories covered by multiple sources
3. Adapts source selection based on platform/topic of interest
4. Summarizes top 5 stories in 2–3 sentences each, in the user's language (KO/EN)
5. Fetches full article on demand for deeper summaries

## Publishing to ClawHub

```bash
npm i -g clawhub
clawhub login
clawhub publish . --slug gamer-news --name "Gamer News" --version 1.0.0 --tags latest
```

## License

MIT
