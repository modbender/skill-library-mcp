# Social Platform Extraction Guide

Tips for extracting maximum data from each platform without authentication.

## Twitter / X

**Profile URL:** `https://twitter.com/<handle>` or `https://x.com/<handle>`

**What to extract:**
- Display name, bio, location field, website link
- Join date (visible on profile)
- Tweet count, followers, following
- Pinned tweet content
- Profile and banner image URLs

**Nitter mirrors (no login required):**
- `https://nitter.net/<handle>`
- `https://nitter.cz/<handle>`
- `https://nitter.privacydev.net/<handle>`

**Search tricks:**
```
site:twitter.com "<name>" → find mentions
from:<handle> → their tweets in Google
to:<handle> → replies to them
```

**Direct tweet search:**
`https://twitter.com/search?q="<query>"&f=live`

---

## Instagram

**Profile URL:** `https://instagram.com/<handle>`

**Public data (no login):**
- Bio, website link, follower counts (partially)
- Post thumbnails visible without login

**Extract via web_fetch:**
`https://www.instagram.com/<handle>/?__a=1` (may require headers)

**Search trick:** `site:instagram.com "<target name>"` in web_search

---

## Reddit

**Profile URL:** `https://reddit.com/user/<handle>`

**What to extract:**
- Account age (karma page shows)
- Post/comment history: `https://reddit.com/user/<handle>/comments`
- Subreddits active in (reveals interests, location clues)
- Pushshift (archived): `https://api.pushshift.io/reddit/search/comment/?author=<handle>`

**Search:** `site:reddit.com/user/<handle>` or `site:reddit.com "<target>"`

---

## LinkedIn

**Profile URL:** `https://linkedin.com/in/<handle>`

**Public data:**
- Name, headline, location
- Current/past employers and roles
- Education
- Skills, endorsements
- Connection count tier (500+, etc.)

**Company search:** `https://linkedin.com/company/<slug>`

**Google dorks:**
```
site:linkedin.com/in "<full name>"
site:linkedin.com/in "<name>" "<company>"
```

---

## GitHub

**Profile URL:** `https://github.com/<handle>`

**What to extract:**
- Real name, bio, company, location, website, Twitter link
- Organisations member of
- Public repos (check README, commits for email leaks)
- Gists: `https://gist.github.com/<handle>`
- Email from commits: `https://api.github.com/users/<handle>/events/public`

**Email from commit:**
```bash
curl -s https://api.github.com/users/<handle>/events/public | python3 -c "
import sys, json
for e in json.load(sys.stdin):
    p = e.get('payload', {})
    for c in p.get('commits', []):
        a = c.get('author', {})
        if a.get('email') and 'noreply' not in a['email']:
            print(a['name'], '-', a['email'])
" 2>/dev/null | sort -u
```

---

## TikTok

**Profile URL:** `https://tiktok.com/@<handle>`

**What to extract:**
- Bio, follower/following/likes counts
- Links in bio
- Video descriptions, hashtags used → reveals interests
- Comments mentioning location

**Search:** `site:tiktok.com "@<handle>"` or `site:tiktok.com "<name>"`

---

## YouTube

**Profile URL:** `https://youtube.com/@<handle>` or `https://youtube.com/channel/<id>`

**What to extract:**
- About page: description, links, join date, view count
- Channel ID (useful for other lookups)
- Playlist names (reveals interests/content themes)

**About page direct:** `https://www.youtube.com/@<handle>/about`

---

## Facebook

**Profile URL:** `https://facebook.com/<handle>` or `https://facebook.com/<numeric_id>`

**Public data (no login, limited):**
- Name, profile photo, cover photo
- Public posts only
- Workplace, education if set to public

**Graph search (limited now):** `https://www.facebook.com/search/top?q=<query>`

**Archive check:** Wayback Machine on `facebook.com/<handle>`

---

## Telegram

**Public channels/groups only:** `https://t.me/<handle>`

**What to extract from public channels:**
- Channel description, member count, post history

**Telegram search tools:**
- `https://tgstat.com/en/search?q=<query>` — channel analytics
- `https://telemetr.io/en` — channel discovery

---

## Discord

Limited public data. Check:
- `disboard.org` for public server listings
- `discord.me` for public server directories
- web_search: `"discord.gg" "<target>"`

---

## Twitch

**Profile URL:** `https://twitch.tv/<handle>`

**API (no key needed):**
```bash
curl -s "https://api.twitch.tv/helix/users?login=<handle>" \
  -H "Client-Id: <public_client_id>"
```

**What to extract:** Bio, stream category, follower count, creation date, connected socials in panels.

---

## Steam

**Profile URL:** `https://steamcommunity.com/id/<handle>` or `/profiles/<steamid64>`

**API (no key needed for public):**
`https://steamcommunity.com/id/<handle>?xml=1`

**SteamDB:** `https://www.steamdb.info/calculator/?player=<handle>`

---

## Image Extraction Tips

### Profile Photo Reverse Search
For any platform profile image:
1. Right-click → copy image URL
2. Feed to: `https://yandex.com/images/search?rpt=imageview&url=<url>`
3. And: `https://tineye.com/search?url=<url>`

### Photo Metadata (EXIF)
If you have the actual image file:
```bash
exiftool <image>          # full metadata
exiftool -gps:all <image> # GPS only
```

Online: `https://www.metadata2go.com` or `https://www.pic2map.com`

### Photo Geolocation Clues
If no EXIF GPS data, analyse visually:
- Street signs, license plates → `web_search` country/region of plate format
- Architecture style, vegetation
- Sun angle → SunCalc.org for time estimation
- Google Street View matching
