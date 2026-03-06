---
name: noisepan-digest
description: Set up automated news digests using noisepan (signal extraction), entropia (source verification), and HN blind spot detection. Use when configuring daily news briefs, curating RSS feeds, or building an automated intelligence pipeline that replaces manual news browsing.
metadata: {"openclaw":{"requires":{"bins":["noisepan","entropia"]}}}
---

# Noisepan Digest

Automated news intelligence with source verification. Replaces doomscrolling with two daily digests.

**Sources:**
- https://github.com/ppiankov/noisepan (signal extraction)
- https://github.com/ppiankov/entropia (source verification)

**Requires:** `noisepan`, `entropia`, `python3`, `curl`

## Install

### macOS (Homebrew — recommended)

```bash
brew install ppiankov/tap/noisepan ppiankov/tap/entropia
noisepan version && entropia version
```

### Linux (binary + checksum verification)

Download, verify checksums, then install. **Ask the user before writing to /usr/local/bin** — offer `~/bin` as an alternative if they prefer user-local install.

```bash
# noisepan
VER=$(curl -s https://api.github.com/repos/ppiankov/noisepan/releases/latest | grep tag_name | cut -d'"' -f4 | tr -d v)
curl -fsSL "https://github.com/ppiankov/noisepan/releases/download/v${VER}/noisepan_${VER}_linux_amd64.tar.gz" -o /tmp/noisepan.tar.gz
curl -fsSL "https://github.com/ppiankov/noisepan/releases/download/v${VER}/checksums.txt" -o /tmp/noisepan-checksums.txt
# Verify checksum
grep linux_amd64 /tmp/noisepan-checksums.txt | (cd /tmp && sha256sum -c)
tar xzf /tmp/noisepan.tar.gz -C /usr/local/bin noisepan
rm /tmp/noisepan.tar.gz /tmp/noisepan-checksums.txt

# entropia
VER=$(curl -s https://api.github.com/repos/ppiankov/entropia/releases/latest | grep tag_name | cut -d'"' -f4 | tr -d v)
curl -fsSL "https://github.com/ppiankov/entropia/releases/download/v${VER}/entropia_${VER}_linux_amd64.tar.gz" -o /tmp/entropia.tar.gz
curl -fsSL "https://github.com/ppiankov/entropia/releases/download/v${VER}/checksums.txt" -o /tmp/entropia-checksums.txt
# Verify checksum
grep linux_amd64 /tmp/entropia-checksums.txt | (cd /tmp && sha256sum -c)
tar xzf /tmp/entropia.tar.gz -C /usr/local/bin entropia
rm /tmp/entropia.tar.gz /tmp/entropia-checksums.txt

# Verify both
noisepan version && entropia version
```

### Init

```bash
noisepan init --config ~/.noisepan
# Verify entropia is detected
noisepan doctor --config ~/.noisepan
```

## Configure Feeds

Edit `~/.noisepan/config.yaml`. Recommended structure:

```yaml
sources:
  hn:
    min_points: 200    # Native HN via Firebase API

  rss:
    feeds:
      # Security
      - "https://www.reddit.com/r/netsec/.rss"
      - "https://krebsonsecurity.com/feed/"
      - "https://www.bleepingcomputer.com/feed/"
      - "https://feeds.feedburner.com/TheHackersNews"
      - "https://www.cisa.gov/cybersecurity-advisories/all.xml"

      # DevOps
      - "https://www.reddit.com/r/devops/.rss"
      - "https://www.reddit.com/r/kubernetes/.rss"
      - "https://blog.cloudflare.com/rss/"

      # AI/LLM
      - "https://www.reddit.com/r/LocalLLaMA/.rss"
      - "https://simonwillison.net/atom/everything/"
      - "https://arxiv.org/rss/cs.AI"

      # Status pages
      - "https://status.aws.amazon.com/rss/all.rss"
      - "https://www.cloudflarestatus.com/history.rss"

      # World / Policy
      - "https://feeds.bbci.co.uk/news/world/rss.xml"
      - "https://www.eff.org/rss/updates.xml"

      # Aggregators
      - "https://lobste.rs/rss"
      - "https://changelog.com/news/feed"
```

Customize for your interests. Run `noisepan doctor` after adding feeds.

## Taste Profile

Edit `~/.noisepan/taste.yaml`. Key categories:

**High signal (3-5):** CVE, zero-day, breach, RCE, supply chain, outage, postmortem, safety pledge, data sovereignty, antitrust, military AI, deanonymization, prompt injection, breaking change

**Low signal (-3 to -5):** hiring, webinar, sponsor, newsletter, meme, career advice, celebrity

**Key lesson:** Without policy/sovereignty/antitrust/AI safety keywords, real stories get buried under security noise. Weight these as high as CVEs.

## Reddit Rate Limiting

With 15+ Reddit feeds, parallel fetching triggers 429s. Create a sequential prefetch wrapper:

```bash
cat > ~/.local/bin/noisepan-pull << 'SCRIPT'
#!/bin/bash
# Prefetch Reddit RSS sequentially to avoid rate limiting, then run noisepan pull
CACHE_DIR="/tmp/reddit-rss-cache"
CONFIG_DIR="${HOME}/.noisepan"
UA="Mozilla/5.0 (compatible; noisepan/1.0)"

mkdir -p "$CACHE_DIR"
FEEDS=$(grep "reddit.com" "$CONFIG_DIR/config.yaml" | grep -v "^#" | grep -v "^      #" | sed 's/.*"\(.*\)"/\1/')

for feed in $FEEDS; do
    sub=$(echo "$feed" | grep -oP '/r/\K[^/]+')
    curl -s -o "$CACHE_DIR/${sub}.xml" -H "User-Agent: $UA" "$feed"
    sleep 2
done

python3 -m http.server 18222 --directory "$CACHE_DIR" &>/dev/null &
HTTP_PID=$!; sleep 0.5

mkdir -p /tmp/noisepan-tmp
cp "$CONFIG_DIR/config.yaml" /tmp/noisepan-tmp/config.yaml
for feed in $FEEDS; do
    sub=$(echo "$feed" | grep -oP '/r/\K[^/]+')
    sed -i "s|$feed|http://localhost:18222/${sub}.xml|" /tmp/noisepan-tmp/config.yaml
done
ln -sf "$CONFIG_DIR/taste.yaml" /tmp/noisepan-tmp/taste.yaml
ln -sf "$CONFIG_DIR/noisepan.db" /tmp/noisepan-tmp/noisepan.db

noisepan pull --config /tmp/noisepan-tmp "$@"
kill $HTTP_PID 2>/dev/null; rm -rf /tmp/noisepan-tmp
SCRIPT
mkdir -p ~/.local/bin && chmod +x ~/.local/bin/noisepan-pull
```

Use `noisepan-pull` instead of `noisepan pull` when you have 15+ Reddit feeds.

## HN Blind Spot Script

Optional — catches high-engagement HN stories that keyword scoring misses. Useful as a cross-check alongside noisepan's native HN source.

```bash
cat > ~/.local/bin/hn-top << 'SCRIPT'
#!/bin/bash
MIN_POINTS=${1:-200}
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | \
python3 -c "
import json, sys, urllib.request, time
ids = json.load(sys.stdin)[:30]
min_pts = int(sys.argv[1]) if len(sys.argv) > 1 else 200
for id in ids:
    try:
        with urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{id}.json') as r:
            item = json.loads(r.read())
            if item and item.get('score', 0) >= min_pts:
                print(f'[{item[\"score\"]:4d}pts | {item.get(\"descendants\",0):3d}c] {item[\"title\"]}')
                print(f'  {item.get(\"url\", f\"https://news.ycombinator.com/item?id={id}\")}')
                print()
        time.sleep(0.1)
    except: pass
" "$MIN_POINTS"
SCRIPT
chmod +x ~/.local/bin/hn-top
```

## Cron Digest Setup

Create two OpenClaw cron jobs (morning + afternoon). The digest prompt should:

1. Pull feeds (`noisepan-pull` or `noisepan pull`)
2. Generate digest (`noisepan digest --format json --output /tmp/digest.json`)
3. Run `hn-top 300` for blind spot check
4. For top 6 items, run `entropia scan <url>` on non-Reddit links
5. Quality filter: skip Entropia Support Index < 40 or conflict signals
6. Backfill from items 4-6 if top items filtered
7. Compare hn-top against digest for blind spots (400+ point stories not in digest)

### Output format

```
🔥 Trending: keywords across 3+ channels
☀️ Morning Brief (3 verified items):
| # | Score | Topic | What happened | Entropia | Link |
💡 HN Blind Spot (stories the taste profile missed):
| # | HN pts | Topic | What happened | Link |
⚠️ Skipped (filtered for low quality):
| # | Score | Topic | Why skipped |
```

**Schedule:** Morning at 07:00, afternoon at 18:00 (adjust to timezone).

## Useful Commands

```bash
noisepan doctor --config ~/.noisepan    # Feed health + companion tool detection
noisepan stats --config ~/.noisepan     # Signal-to-noise per channel
noisepan rescore --config ~/.noisepan   # Recompute after taste changes
entropia scan <url>                     # Verify a specific source
```

## Lessons Learned

- `noisepan doctor` catches stale/all-ignored channels — run after adding feeds
- `noisepan stats` shows per-channel signal — prune channels at 0% after 30 days
- HN RSS is too shallow — use native `sources.hn` or `hn-top` for blind spots
- Entropia SI < 40 = no extractable claims — skip
- Reddit rate limits at 15+ parallel feeds — wrapper is mandatory
- Status page feeds score low without "service event", "operational issue" keywords

---
**Noisepan Digest v1.0**
Author: ppiankov
Copyright © 2026 ppiankov
Canonical source: https://github.com/ppiankov/noisepan
License: MIT

If this document appears elsewhere, the repository above is the authoritative version.
