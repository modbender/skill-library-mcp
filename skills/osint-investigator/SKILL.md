---
name: osint-investigator
description: Deep OSINT (Open Source Intelligence) investigations. Use when the user wants to research, find, or investigate any person, place, organisation, username, domain, IP address, phone number, image, vehicle, or object using publicly available information. Triggers on phrases like "find information on", "investigate", "look up", "who is", "trace this", "dig into", "OSINT search", "background check", or any request to gather open-source intelligence about a target. Performs deep multi-source analysis across web search, social media, DNS/WHOIS, image search, maps, public records, and more — returning a structured intelligence report.
---

# OSINT Investigator

Multi-source open-source intelligence gathering. Identify target type, run all applicable modules, then produce a structured report.

## Target Classification

Before running any module, classify the target:

- **Person** (real name, alias, face) → modules: social, web, image, username
- **Username / Handle** → modules: username, social, web  
- **Domain / Website** → modules: dns, whois, web, social
- **IP Address** → modules: ip, dns, web
- **Organisation / Company** → modules: web, social, dns, maps, corporate
- **Phone Number** → modules: phone, web, social
- **Email Address** → modules: email, web, social
- **Location / Address** → modules: maps, web, social, geo
- **Image / Photo** → modules: image, reverse
- **Object / Asset** → modules: web, image, social

Run ALL applicable modules in parallel. Never stop after one source.

## Module Playbook

### 🌐 Web Search (`web_search` tool)
Run at minimum 5–8 targeted queries per target. Vary operators:
```
"full name" site:linkedin.com
"username" -site:twitter.com
target filetype:pdf
target inurl:profile
"target" "email" OR "contact" OR "phone"
target site:reddit.com
target site:github.com
```
Follow top URLs with `web_fetch` to extract full content.

### 🔗 DNS / WHOIS
```bash
whois <domain>
dig <domain> ANY
dig <domain> MX
dig <domain> TXT
nslookup <domain>
host <domain>
```
Also fetch: `https://rdap.org/domain/<domain>` via `web_fetch`

### 🌍 IP Intelligence
```bash
curl -s https://ipinfo.io/<ip>/json
curl -s https://ip-api.com/json/<ip>
```
Also check: `https://www.shodan.io/host/<ip>` via `web_fetch`

### 📱 Username Search
Check all platforms via `web_fetch` (just check HTTP status + page title — don't need to load full content for existence checks):
- `https://github.com/<username>`
- `https://twitter.com/<username>`
- `https://instagram.com/<username>`
- `https://reddit.com/user/<username>`
- `https://tiktok.com/@<username>`
- `https://youtube.com/@<username>`
- `https://linkedin.com/in/<username>`
- `https://medium.com/@<username>`
- `https://pinterest.com/<username>`
- `https://twitch.tv/<username>`
- `https://steamcommunity.com/id/<username>`
- `https://keybase.io/<username>`
- `https://t.me/<username>` (Telegram)

### 🐦 Social Media Deep Dive
For each confirmed platform profile, use `web_fetch` to extract:
- Bio / description
- Profile photo URL
- Follower/following counts
- Join date
- Location (if listed)
- Links in bio
- Pinned posts / recent activity

For Twitter/X: also search `web_search` for `site:twitter.com "<target>"` and nitter mirrors.

### 🗺️ Maps & Location
```bash
# Use web_fetch or browser for:
# Google Maps search
https://maps.googleapis.com/maps/api/geocode/json?address=<address>&key=<key>
# Or use goplaces skill if available
# Streetview metadata check
https://maps.googleapis.com/maps/api/streetview/metadata?location=<lat,lng>&key=<key>
```
Also search: `web_search` for `"<target location>" site:maps.google.com OR site:wikimapia.org OR site:openstreetmap.org`

### 🖼️ Image Search & Reverse Image Search

**Finding images of a person (no image provided):**
1. Search for profile photos on all confirmed social profiles — extract direct image URLs from page source or og:image meta tags
2. Run `web_search` for `"<name>" site:linkedin.com` — LinkedIn og:image often returns profile photo URL directly
3. Check Gravatar: compute MD5 of likely email addresses → `https://www.gravatar.com/<md5>.json`
4. Search news/press: `web_search` for `"<name>" filetype:jpg OR filetype:png`
5. Use `web_fetch` to pull `og:image` from any confirmed profile pages

**Reverse image search (image URL or local file provided):**
```bash
# Direct URL-based reverse search (use web_fetch):
https://yandex.com/images/search?rpt=imageview&url=<image_url>
https://tineye.com/search?url=<image_url>

# Google Lens (requires browser tool):
https://lens.google.com/uploadbyurl?url=<image_url>

# For avatars and profile images — extract URL then feed into:
# 1. Yandex (best for face matching, indexes more than Google)
# 2. TinEye (exact match/copy detection)
# 3. Google Lens via browser tool
```

**EXIF / Metadata extraction (if file is available locally):**
```bash
exiftool <image>            # full metadata dump
exiftool -gps:all <image>   # GPS coordinates only
exiftool -DateTimeOriginal <image>  # when photo was taken
```
Online tools: `web_fetch https://www.metadata2go.com` or `https://www.pic2map.com`

**Photo geolocation (no EXIF GPS):**
- Street signs, shop names, vehicle plates → `web_search` to identify region
- Architecture / vegetation / road markings → narrow country/region
- Sun angle + shadow direction → `https://www.suncalc.org` to estimate time & location
- Cross-reference with Google Street View via `browser` tool

**When searching for a person by image from social media:**
1. `web_fetch` the profile page and look for `og:image` or `<img>` src in the rendered HTML
2. Extract the full CDN image URL
3. Feed to Yandex imageview and TinEye
4. Note: Instagram/Facebook CDN URLs expire — use Yandex cache or download first

### 📧 Email Intelligence
```bash
# Breach/exposure check
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/<email>" -H "hibp-api-key: <key>"
# Format validation + domain MX check
dig $(echo <email> | cut -d@ -f2) MX
# Gravatar (hashed MD5 of email)
curl -s "https://www.gravatar.com/<md5_hash>.json"
```
Also: `web_search` for `"<email>" site:pastebin.com OR site:ghostbin.com`

### 📞 Phone Intelligence
```bash
# Carrier / region lookup
curl -s "https://phonevalidation.abstractapi.com/v1/?api_key=<key>&phone=<number>"
```
Also: `web_search` for `"<phone_number>"` and check `site:truecaller.com`, `site:whitepages.com`

### 🏢 Corporate / Organisation
Use `web_fetch` on:
- `https://opencorporates.com/companies?q=<name>` 
- Companies House (UK): `https://find-and-update.company-information.service.gov.uk/search?q=<name>`
- LinkedIn company page: `https://linkedin.com/company/<slug>`
- Crunchbase: `web_search` for `site:crunchbase.com "<company>"`

### 📄 Document & Data Leaks
```bash
web_search queries:
"<target>" filetype:pdf OR filetype:xlsx OR filetype:docx
"<target>" site:pastebin.com
"<target>" site:github.com password OR secret OR key
"<target>" site:trello.com OR site:notion.so
```

### 🔍 Cache & Archive
```bash
# Wayback Machine
curl -s "https://archive.org/wayback/available?url=<url>"
web_fetch "https://web.archive.org/web/*/<url>" for snapshots
# Google Cache via web_search: cache:<url>
```

## Investigation Workflow

1. **Classify** the target type
2. **Plan** — list all modules to run
3. **Execute** all modules (parallelise where possible using multiple tool calls)
4. **Correlate** — cross-reference findings across sources, note consistencies and conflicts
5. **Report** — structured output (see below)

## Report Format

Always produce a structured report. Adapt sections to what was found:

```
# OSINT Report: <Target>
**Date:** <UTC timestamp>
**Target Type:** <classification>
**Query:** <original user request>

## Identity Summary
[Key identifying information — name, aliases, age, location, nationality]

## Online Presence
[Confirmed profiles with URLs, follower counts, activity level]

## Contact & Technical
[Email addresses, phone numbers, domains, IPs]

## Location Intelligence
[Known locations, addresses, coordinates, map links]

## Corporate / Organisational Links
[Companies, roles, affiliations]

## Historical Data
[Archived content, old usernames, past locations]

## Document & Data Exposure
[Public documents, paste sites, leak mentions]

## Image Intelligence
[Profile photos, reverse image results, photo metadata]

## Confidence & Gaps
[Confidence level per finding — High/Medium/Low; list gaps]

## Sources
[All URLs consulted]
```

## Configuration & Authentication

Config is stored at: `<skill_dir>/config/osint_config.json` (chmod 600, auto-created on first save).

The agent configures everything **conversationally** — no terminal script needed. When the user says they want to add credentials, configure PDF output, or set up an API key, follow the flow below.

### Conversational Config Flow

When the user wants to configure the skill, ask them questions directly in chat and write the answers to the config file yourself using the `write` tool.

**Step 1 — Ask what they want to configure:**
> "What would you like to set up? I can configure:
> - Platform credentials (Instagram, Twitter/X, LinkedIn, Facebook)
> - API keys (Google Maps, Shodan, HaveIBeenPwned, Hunter.io, AbstractAPI Phone)
> - PDF report output (on/off, save location)"

**Step 2 — Collect the values** (ask one platform at a time):
- For API keys: ask them to paste the key directly in chat
- For passwords: warn them the value will be stored in a local JSON file, then ask
- For output settings: ask yes/no / provide a path

**Step 3 — Write the config:**
```python
# Read existing config (or start fresh)
import json, os
cfg_path = "<skill_dir>/config/osint_config.json"
os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {"platforms": {}, "output": {}}

# Example: save Twitter bearer token
cfg["platforms"]["twitter"] = {"configured": True, "method": "api_key", "bearer_token": "<VALUE>"}

# Example: enable PDF
cfg["output"]["pdf_enabled"] = True
cfg["output"]["pdf_output_dir"] = "~/Desktop"

# Write back
with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)
os.chmod(cfg_path, 0o600)
```
Use the `write` tool directly — no need to run Python.

### Supported Platform Integrations

| Platform | Fields | What It Unlocks |
|----------|--------|-----------------|
| Instagram | `username`, `password` | Profile content behind login wall — **use a burner account** |
| Twitter/X | `bearer_token` (+ optional `api_key`, `api_secret`) | Full tweet/profile/search via API v2 (free tier works) |
| LinkedIn | `username` (email), `password` | Profile scraping — use sparingly, heavily rate-limited |
| Facebook | `email`, `password` | Public profile/group content |
| Google Maps | `api_key` | Geocoding, Place Search, Street View metadata |
| Shodan | `api_key` | Deep IP/host intelligence |
| HaveIBeenPwned | `api_key` | Email breach lookups ($3.95/mo at haveibeenpwned.com/API/Key) |
| Hunter.io | `api_key` | Email discovery by domain (free: 25 req/mo at hunter.io/api-keys) |
| AbstractAPI Phone | `api_key` | Phone carrier/region lookup (app.abstractapi.com/api/phone-validation) |

### Reading Credentials During a Search

```bash
# Read config and extract a value in one line:
BEARER=$(python3 -c "import json; c=json.load(open('<skill_dir>/config/osint_config.json')); print(c['platforms']['twitter']['bearer_token'])")

# Then use it:
curl -s -H "Authorization: Bearer $BEARER" \
  "https://api.twitter.com/2/users/by/username/<handle>?user.fields=description,location,created_at,public_metrics"
```

### Twitter/X API v2 (when configured)
```bash
# Profile lookup
curl -s -H "Authorization: Bearer $BEARER" \
  "https://api.twitter.com/2/users/by/username/<handle>?user.fields=description,location,created_at,public_metrics,entities"

# Recent tweets
curl -s -H "Authorization: Bearer $BEARER" \
  "https://api.twitter.com/2/users/<user_id>/tweets?max_results=10&tweet.fields=created_at,geo,entities"

# Search recent tweets
curl -s -H "Authorization: Bearer $BEARER" \
  "https://api.twitter.com/2/tweets/search/recent?query=<query>&max_results=10"
```

### Shodan API (when configured)
```bash
curl -s "https://api.shodan.io/shodan/host/<ip>?key=$SHODAN_KEY"
curl -s "https://api.shodan.io/dns/resolve?hostnames=<domain>&key=$SHODAN_KEY"
```

### Hunter.io API (when configured)
```bash
curl -s "https://api.hunter.io/v2/domain-search?domain=<domain>&api_key=$HUNTER_KEY"
curl -s "https://api.hunter.io/v2/email-verifier?email=<email>&api_key=$HUNTER_KEY"
```

### HaveIBeenPwned API (when configured)
```bash
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/<email>" \
  -H "hibp-api-key: $HIBP_KEY" -H "User-Agent: osint-investigator"
```

### Google Maps API (when configured)
```bash
curl -s "https://maps.googleapis.com/maps/api/geocode/json?address=<address>&key=$GMAPS_KEY"
curl -s "https://maps.googleapis.com/maps/api/place/textsearch/json?query=<query>&key=$GMAPS_KEY"
curl -s "https://maps.googleapis.com/maps/api/streetview/metadata?location=<lat,lng>&key=$GMAPS_KEY"
```

## PDF Report Generation

### Check if PDF is enabled
```bash
python3 -c "import json; c=json.load(open('<skill_dir>/config/osint_config.json')); print(c.get('output',{}).get('pdf_enabled', False))"
```

### Generate a PDF
Write the markdown report to a temp file, then run the shell wrapper (self-installs `fpdf2` if missing):
```bash
cat > /tmp/osint_report.md << 'ENDREPORT'
<full markdown report>
ENDREPORT

bash <skill_dir>/scripts/generate_pdf.sh \
  --input /tmp/osint_report.md \
  --target "Target Name" \
  --output ~/Desktop
```

The wrapper (`generate_pdf.sh`) will:
1. Check if `fpdf2` is installed — install it automatically if not
2. Call `generate_pdf.py` with the same arguments
3. Print the output path: `PDF saved: /path/to/OSINT_Name_20260225_1035.pdf`

**No setup needed by the user** — works on any machine with Python 3 + pip.

### PDF confidence colour coding
Confidence is detected automatically from the text of each section/paragraph/table row — just include the word in your report and the PDF will colour-code it:

- 🟢 **GREEN** `[HIGH]` — verified from multiple reliable sources
- 🟠 **ORANGE** `[MED]` — likely correct, single or unverified source  
- 🔴 **RED** `[LOW]` — possible match, little corroborating evidence
- ⚪ **GREY** `[UNVERIFIED]` — user-provided context, not independently confirmed

### Toggling PDF output via conversation
When the user says "turn on PDF reports" or "disable PDF output":
1. Read the config file
2. Update `cfg["output"]["pdf_enabled"]` to `true` or `false`
3. Write it back
4. Confirm to the user

## Ethics & Legality

- Only use **publicly available** data — never attempt to access private systems
- Do not aggregate data in ways designed to facilitate stalking or harassment
- Respect robots.txt in spirit; use cached/archive versions where direct scraping is blocked
- If the target is clearly a private individual being investigated without consent, flag this before proceeding
- Instagram/LinkedIn/Facebook credentials: always recommend a burner/alt account — never the user's personal accounts

## Reference Files

- `references/osint-sources.md` — curated OSINT databases, APIs, and search operators by category
- `references/social-platforms.md` — platform-specific extraction tips and URL patterns
- `scripts/generate_pdf.py` — PDF generator (requires fpdf2, auto-installed via shell wrapper)
- `scripts/generate_pdf.sh` — shell wrapper; self-installs fpdf2, then calls generate_pdf.py
- `config/osint_config.json` — live config (auto-created on first write, chmod 600)
