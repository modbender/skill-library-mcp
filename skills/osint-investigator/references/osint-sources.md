# OSINT Sources — Master Reference

## Search Engines & General
| Source | URL | Notes |
|--------|-----|-------|
| Google | `https://google.com` | Use `web_search` tool; operators: `site:`, `inurl:`, `filetype:`, `"exact"`, `-exclude` |
| Bing | `https://bing.com` | Indexes different content to Google |
| DuckDuckGo | `https://duckduckgo.com` | Less filtered results |
| Yandex | `https://yandex.com` | Excellent for Eastern European targets; superior reverse image |
| Startpage | `https://startpage.com` | Google proxy, no tracking |
| Wayback Machine | `https://web.archive.org` | Historical snapshots: `https://web.archive.org/web/*/<url>` |
| Cached pages | `cache:<url>` in Google | Snapshot of last crawl |

## Social Media
| Platform | Profile URL | Search URL |
|----------|-------------|------------|
| Twitter/X | `twitter.com/<handle>` | `twitter.com/search?q=<query>` |
| Instagram | `instagram.com/<handle>` | Use web_search: `site:instagram.com "<term>"` |
| Facebook | `facebook.com/<handle>` | Public pages/profiles only |
| LinkedIn | `linkedin.com/in/<handle>` | `linkedin.com/company/<slug>` for orgs |
| TikTok | `tiktok.com/@<handle>` | |
| Reddit | `reddit.com/user/<handle>` | `reddit.com/search?q=<query>` |
| YouTube | `youtube.com/@<handle>` | |
| Twitch | `twitch.tv/<handle>` | |
| GitHub | `github.com/<handle>` | Check repos, gists, commits for email addresses |
| Telegram | `t.me/<handle>` | Public channels/groups only |
| Pinterest | `pinterest.com/<handle>` | |
| Snapchat | `snapchat.com/add/<handle>` | Limited public data |
| Medium | `medium.com/@<handle>` | |
| Substack | `<handle>.substack.com` | |
| Mastodon | Federated — search `<handle>@<instance>` | |

## Username Search Aggregators
| Tool | URL |
|------|-----|
| Namechk | `https://namechk.com/<username>` |
| Knowem | `https://knowem.com/<username>` |
| Sherlock (if installed) | `sherlock <username>` |
| WhatsMyName | `https://whatsmyname.app` |

## Domain & DNS Intelligence
| Tool | Command / URL |
|------|---------------|
| WHOIS | `whois <domain>` |
| RDAP | `https://rdap.org/domain/<domain>` |
| Dig | `dig <domain> ANY/MX/TXT/NS` |
| DNSDumpster | `https://dnsdumpster.com` (web_fetch) |
| SecurityTrails | `https://securitytrails.com/domain/<domain>/dns` |
| Shodan | `https://www.shodan.io/search?query=<domain>` |
| BuiltWith | `https://builtwith.com/<domain>` — tech stack |
| Wappalyzer | Browser extension / `https://www.wappalyzer.com/lookup/<domain>` |
| crt.sh | `https://crt.sh/?q=<domain>` — SSL cert transparency |
| ViewDNS | `https://viewdns.info` — reverse IP, reverse whois |
| DomainTools | `https://whois.domaintools.com/<domain>` |

## IP Address Intelligence
| Tool | URL / Command |
|------|---------------|
| IPInfo | `https://ipinfo.io/<ip>/json` |
| IP-API | `https://ip-api.com/json/<ip>` |
| AbuseIPDB | `https://www.abuseipdb.com/check/<ip>` |
| Shodan | `https://www.shodan.io/host/<ip>` |
| GreyNoise | `https://viz.greynoise.io/ip/<ip>` |
| BGP.tools | `https://bgp.tools/prefix/<ip>` |
| IPVoid | `https://www.ipvoid.com/ip-blacklist-check/` |

## Email Intelligence
| Tool | URL / Command |
|------|---------------|
| HaveIBeenPwned | `https://haveibeenpwned.com/api/v3/breachedaccount/<email>` (needs API key) |
| Hunter.io | `https://hunter.io/email-finder` — find emails by domain |
| Gravatar | `https://www.gravatar.com/<MD5_of_email>.json` |
| EmailRep | `https://emailrep.io/<email>` |
| Holehe (if installed) | `holehe <email>` — checks account existence on 100+ sites |

## Phone Number Intelligence  
| Tool | URL |
|------|-----|
| Truecaller | `https://www.truecaller.com/search/us/<number>` |
| Sync.me | `https://sync.me/search/?number=<number>` |
| PhoneInfoga (if installed) | `phoneinfoga scan -n <number>` |
| AbstractAPI | `https://phonevalidation.abstractapi.com/v1/?phone=<number>` |
| NumVerify | `https://numverify.com/api/validate?number=<number>` |

## Image & Face Intelligence
| Tool | URL |
|------|-----|
| Google Images | `https://images.google.com` — use browser to upload |
| Yandex Images | `https://yandex.com/images/search?rpt=imageview&url=<url>` |
| TinEye | `https://tineye.com/search?url=<url>` |
| Bing Visual Search | `https://www.bing.com/visualsearch` |
| PimEyes (face) | `https://pimeyes.com` — face recognition (limited free) |
| FaceCheck.ID | `https://facecheck.id` |

## Maps & Geolocation
| Tool | URL |
|------|-----|
| Google Maps | `https://www.google.com/maps/search/<query>` |
| OpenStreetMap | `https://www.openstreetmap.org/search?query=<address>` |
| Google StreetView | `https://www.google.com/maps/@<lat>,<lng>,3a,75y,90t/data=...` |
| Wikimapia | `https://wikimapia.org/#lat=<lat>&lon=<lng>` |
| SunCalc | `https://www.suncalc.org` — verify photo time from sun angle |
| GeoHack | `https://geohack.toolforge.org/geohack.php?params=<lat>_N_<lng>_E` |

## Corporate / Company Records
| Tool | URL | Coverage |
|------|-----|----------|
| OpenCorporates | `https://opencorporates.com/companies?q=<name>` | Global |
| Companies House | `https://find-and-update.company-information.service.gov.uk/search?q=<name>` | UK |
| SEC EDGAR | `https://efts.sec.gov/LATEST/search-index?q=<name>` | US public companies |
| Crunchbase | `https://www.crunchbase.com/search/organizations/field/organizations/facet_ids/<query>` | Startups/VC |
| LinkedIn | `https://www.linkedin.com/company/<slug>` | |
| Pitchbook | Web search: `site:pitchbook.com "<company>"` | |

## Paste & Leak Sites
| Site | URL |
|------|-----|
| Pastebin | `https://pastebin.com/search?q=<query>` |
| GitHub Gists | `https://gist.github.com/search?q=<query>` |
| JustPaste.it | web_search: `site:justpaste.it "<target>"` |
| ControlC | web_search: `site:controlc.com "<target>"` |
| Rentry | web_search: `site:rentry.co "<target>"` |
| DeHashed | `https://dehashed.com/search?query=<email>` (paid, but check for public results) |

## Public Records (UK-focused for Finley)
| Source | URL |
|--------|-----|
| 192.com | `https://www.192.com/search/people/<name>` |
| BT Phone Book | `https://www.thephonebook.bt.com` |
| Electoral Roll | via 192.com or Tracesmart |
| UK Land Registry | `https://www.gov.uk/search-property-information-land-registry` |
| UK Court Records | `https://www.find-court-tribunal.service.gov.uk` |
| Companies House | `https://find-and-update.company-information.service.gov.uk` |

## Google Dorking Operators
```
site:          - restrict to domain
inurl:         - keyword in URL
intitle:       - keyword in page title  
filetype:      - specific file type (pdf, xlsx, docx, txt)
"exact phrase" - exact match
-keyword       - exclude keyword
OR             - either term
*              - wildcard
before:YYYY    - results before date
after:YYYY     - results after date
cache:         - Google's cached version
related:       - similar sites
```

### High-value dorks
```
"<target>" filetype:pdf              # documents mentioning target
"<target>" site:github.com           # code references
"<target>" site:pastebin.com         # paste leaks
"<target>" "password" OR "passwd"    # credential exposure
"<target>" "email" filetype:xlsx     # spreadsheet leaks
"<target>" inurl:admin OR inurl:login # admin panels
"<name>" "@gmail.com" OR "@yahoo.com" # email discovery
```
