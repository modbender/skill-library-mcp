# Recon — Structured Reconnaissance Methodology

This file guides the **RECON phase** (Phase 1) of every engagement. Complete this before jumping into vulns. Recon quality directly determines audit quality.

> **Important:** Do NOT actively probe out-of-scope assets. Passive recon is always safe. Active recon (port scans, fuzzing) should only target **in-scope** assets confirmed from the program rules.

---

## Phase 1A — Parse the Program

Before touching any target:

1. **Run `scripts/analyze_scope.py`** on the program file if available:
   ```
   python scripts/analyze_scope.py <program_file.md> --output scope.json
   ```

2. **Manually confirm:**
   - Exact in-scope domains/wildcards (`*.target.com` vs `app.target.com`)
   - Out-of-scope subdomains (often `corporate.target.com`, `careers.target.com`)
   - Excluded vuln types (self-XSS? rate limiting? CSP headers?)
   - Reward tiers — focus time on P1/P2 targets first
   - Special rules (no automated scanning? max request rate?)

3. **Identify the platform** — note which report format to use (`references/platforms/`)

---

## Phase 1B — Passive Subdomain Enumeration

**Goal:** Map all subdomains without sending a single packet to the target.

**Tools to suggest to user (passive only):**

| Tool | Command | What It Finds |
|---|---|---|
| Amass (passive) | `amass enum -passive -d target.com` | DNS, certificates, APIs |
| Subfinder | `subfinder -d target.com -silent` | Passive DNS aggregation |
| crt.sh | `curl https://crt.sh/?q=%25.target.com&output=json` | Certificate transparency |
| Wayback Machine | `gau target.com \| grep -oP '(?<=://)[\w.-]+\.target\.com' \| sort -u` | Historical subdomains |
| SecurityTrails | Search `*.target.com` manually (free tier) | DNS history, MX, NS |
| Shodan | `ssl:"target.com"` or `hostname:target.com` | Exposed services |
| VirusTotal | Search domain in VT graph | Historical DNS |

**After collecting subdomains — resolve live ones:**
```
cat subdomains.txt | dnsx -silent -a -resp > live_subdomains.txt
```

**Check for interesting patterns:**
- `api.target.com`, `api-v2.`, `api-internal.` — API endpoints
- `admin.`, `dashboard.`, `backstage.`, `internal.` — admin panels
- `dev.`, `staging.`, `test.`, `beta.`, `preprod.` — dev environments (looser security)
- `vpn.`, `remote.`, `jira.`, `confluence.` — internal tools potentially exposed
- `cdn.`, `assets.`, `static.` — CDN subdomains (usually out of scope for vulns)

---

## Phase 1C — Technology Fingerprinting

**Goal:** Understand the tech stack before targeting specific vuln classes.

**Passive fingerprinting:**
- **Wappalyzer** (browser extension) — detects framework, CMS, JS libraries, server
- **Stack check from response headers:**
  - `X-Powered-By: Express` → Node.js
  - `X-Powered-By: PHP/8.1` → PHP version
  - `Server: nginx/1.20.1` → Nginx version
  - `X-AspNet-Version` → .NET
  - `Set-Cookie: JSESSIONID=` → Java
  - `Set-Cookie: laravel_session=` → Laravel/PHP
  - `Set-Cookie: csrftoken=` → Django/Python

**JS framework detection (check page source):**
- `__NEXT_DATA__` in page source → Next.js
- `window.__NUXT__` → Nuxt.js
- `ng-version` attribute → Angular
- `data-reactroot` → React
- `__vue_async_data` → Vue.js

**Auth protocol detection:**
- OAuth 2.0: Look for `/oauth/authorize`, `/oauth/token`, `client_id=` in URLs
- SAML: Look for `SAMLRequest=` in URLs
- JWT: Check Authorization headers, cookies named `token`, `jwt`, `access_token`
- API keys: `X-API-Key`, `api_key=` in requests

---

## Phase 1D — JavaScript Bundle Analysis

**The single most underutilized recon step.** Modern SPAs bundle their entire codebase into JS files accessible in the browser — including API endpoints, internal paths, and sometimes hardcoded credentials.

**Step 1 — Find JS bundles:**
```
# From browser DevTools → Sources tab → look for main.*.js, chunk.*.js
# Or from page source: grep for <script src="...js">
```

**Step 2 — Extract endpoints and interesting strings:**
```bash
# Download all JS bundles
gau https://target.com | grep '\.js$' | wget -i -

# Extract API paths
grep -oP '["\x27](/[a-z0-9_/-]{3,})["\x27]' *.js | sort -u

# Find secrets / credentials
grep -iE 'api_key|secret|password|token|credential|bearer|auth' *.js

# Find internal URLs
grep -oP 'https?://[^\s"]+internal[^\s"]+' *.js
```

**Tool to suggest:** [LinkFinder](https://github.com/GerbenJavado/LinkFinder) — automated JS endpoint extractor:
```
python linkfinder.py -i https://target.com/static/js/main.js -o cli
```

**What to look for:**
- Hidden API routes not in official docs
- Internal hostnames (`http://internal-api.target.local`)
- Hardcoded API keys, `REACT_APP_SECRET_KEY=`, `AWS_ACCESS_KEY=`
- Feature flags referencing unreleased/admin features
- Debug endpoints (`/debug/`, `/admin/`, `/__debug__/`)

---

## Phase 1E — Active Endpoint Discovery

**Only perform on confirmed in-scope assets after passive recon.**

**HTTP probing live subdomains:**
```
httpx -l live_subdomains.txt -title -status-code -tech-detect -o live_http.txt
```

**Directory/endpoint fuzzing (targeted, not aggressive):**
```
# API endpoint fuzzing
ffuf -u https://api.target.com/FUZZ -w /path/to/api_wordlist.txt -mc 200,301,302,403 -o api_endpoints.json

# Standard directory fuzzing
ffuf -u https://target.com/FUZZ -w /path/to/common.txt -mc 200,301,302 -t 50
```

**Useful wordlists:**
- `/usr/share/seclists/Discovery/Web-Content/api/objects.txt`
- `/usr/share/seclists/Discovery/Web-Content/common.txt`
- `/usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt`

**Check these paths on every target:**
```
/.env, /.git/config, /.git/HEAD
/swagger.json, /api/swagger.json, /openapi.yaml, /api-docs
/graphql, /graphiql, /api/graphql
/admin, /administrator, /dashboard, /backstage
/debug, /status, /health, /metrics, /actuator (Spring Boot)
/v1/, /v2/, /api/v1/, /api/v2/
/robots.txt (reveals paths to not crawl — often reveals interesting endpoints)
/sitemap.xml
```

---

## Phase 1F — Attack Surface Mapping

After collecting all the above, build an attack surface map:

```
TARGET SURFACE MAP
==================
Primary app:    https://app.target.com [React, Node.js Express, PostgreSQL]
Auth:           OAuth 2.0 via /oauth/authorize, JWT in Bearer header
API:            https://api.target.com/v2/ (Swagger at /api/v2/docs)
Admin panel:    https://admin.target.com (behind SSO — test SSO bypass)
Dev/staging:    https://staging.target.com (resolves — SAME codebase, less protections?)
GraphQL:        https://app.target.com/graphql (introspection open)
File uploads:   POST /api/v2/users/avatar, POST /api/v2/documents/upload
Interesting JS: Found /api/v2/admin/impersonate in main.js — not in docs
```

---

## Phase 1G — Information Disclosure Checks

Quick wins before deep vuln hunting:

| Target | What to Check |
|---|---|
| `/.git/config` | Exposed git repo — clone it: `git clone https://target.com/.git` |
| `/.env` | Database URLs, API keys, encryption secrets |
| `/robots.txt` | Paths marked `Disallow` — often admin/sensitive routes |
| `/sitemap.xml` | Full URL list of the application |
| Error messages | Stack traces, SQL errors, path disclosure |
| HTML comments | `<!-- TODO: remove before prod -->`, internal paths, credentials |
| `X-Debug-Token` header | Symfony profiler exposed |
| `/actuator/env` | Spring Boot — full environment variables including secrets |
| `/actuator/heapdump` | Spring Boot — download heap → extract secrets |
| Response headers | `X-Powered-By`, `Server` version info for known CVEs |

---

## Recon Output Checklist

Before moving to Phase 2 (Audit), confirm you have:

- [ ] In-scope asset list confirmed from program rules
- [ ] Live subdomains enumerated and HTTP-probed
- [ ] Technology stack identified per asset
- [ ] JS bundles downloaded and endpoint-extracted
- [ ] Swagger/OpenAPI schema downloaded if available
- [ ] GraphQL introspection attempted
- [ ] Low-hanging info disclosure checked (`.env`, `.git`, `robots.txt`)
- [ ] Dev/staging instances noted (test separately — often less protected)
- [ ] Attack surface map written down (even a simple bullet list)
- [ ] Highest-reward focus areas identified (from reward tier analysis)
