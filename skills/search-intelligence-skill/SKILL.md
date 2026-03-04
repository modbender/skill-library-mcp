---
name: search-intelligence-skill
description: Advanced AI-powered search skill using SearXNG as the universal search backend. Multi-engine dork generation, 90+ search engines, intelligent search strategies, intent parsing, result analysis, and adaptive query refinement. No API keys required.
metadata: {"clawdbot":{"emoji":"🕵️","requires":{"python":">=3.9","packages":["httpx>=0.27.0"]},"install":[{"id":"pip","kind":"pip","package":"search-intelligence-skill","label":"Install search-intelligence-skill (pip)"},{"id":"local","kind":"local","command":"pip install -e .","label":"Install from source"}]}}
---

# search-intelligence-skill

Use `search-intelligence-skill` to give any AI agent the ability to search the entire internet like an expert OSINT analyst, SEO engineer, and security researcher combined. All searches flow through your SearXNG instance — zero API keys, full privacy, 90+ engines.

The skill generates optimized dork queries, selects intelligent multi-step search strategies, translates operators across engines, routes queries to the best SearXNG engines, scores results by multi-signal relevance, and learns from results to refine searches automatically.

## Setup (once)

**Install the package**
```bash
# From source (recommended)
git clone https://github.com/mouaad-ops/search-intelligence-skill.git
cd search-intelligence-skill
pip install -e .

# Or direct pip
pip install search-intelligence-skill # NOT yet working
```

**Start a SearXNG instance (if you don't have one)**
```bash
# Docker (quickest)
docker run -d \
  --name searxng \
  -p 8888:8080 \
  -e SEARXNG_SECRET=your-secret-key \
  searxng/searxng:latest

# Verify it's running
curl http://localhost:8888/healthz
```

**Enable JSON API in SearXNG settings**
```yaml
# In searxng/settings.yml — ensure search formats include json
search:
  formats:
    - html
    - json
```

**Initialize in code**
```python
from search_intelligence_skill import SearchSkill

# Default — localhost:8888
skill = SearchSkill()

# Custom instance
skill = SearchSkill(
    searxng_url="http://localhost:8888",
    timeout=30.0,
    max_retries=2,
    rate_limit=0.5,
    verify_ssl=True,
    auto_refine=True,
    max_refine_rounds=1,
)

# Verify connection
if skill.health_check():
    print("✓ SearXNG is reachable")
else:
    print("✗ Cannot reach SearXNG — check URL and port")
```

## Common Commands

**Natural language search (the main interface)**
```python
from search_intelligence_skill import SearchSkill

skill = SearchSkill(searxng_url="http://localhost:8888")

# Just describe what you want — the skill handles everything:
# intent detection, dork generation, engine selection, scoring
report = skill.search("find exposed .env files on example.com")

# Print LLM-ready formatted output
print(report.to_context())

# Access structured results
for r in report.top(5):
    print(f"[{r.relevance:.1f}] {r.title}")
    print(f"    {r.url}")
    print(f"    {r.snippet[:200]}")
```

**Control search depth**
```python
from search_intelligence_skill import Depth

# Quick — 1-2 queries, single step, fast lookup
report = skill.search("what is CORS", depth="quick")

# Standard — 3-6 queries, multi-engine, good default
report = skill.search("python async frameworks comparison", depth="standard")

# Deep — 6-12 queries, multi-step strategies, thorough research
report = skill.search("security audit of target.com", depth="deep")

# Exhaustive — 12+ queries, full OSINT chains, complete sweep
report = skill.search("full recon on suspect-domain.com", depth="exhaustive")
```

**Security scanning — exposed files and panels**
```python
report = skill.search(
    "find exposed .env files, admin panels, and directory listings on example.com",
    depth="deep",
)

print(f"Intent: {report.intent.category.value}/{report.intent.subcategory}")
# → Intent: security/exposed_files

print(f"Strategy: {report.strategy.name}")
# → Strategy: multi_angle

print(f"Results: {len(report.results)}")
for r in report.top(10):
    print(f"  [{r.relevance:.1f}] {r.title} — {r.url}")
```

**Security scanning — vulnerability research**
```python
# CVE research
report = skill.search("CVE-2024-3094 xz backdoor exploit details", depth="deep")

# Technology-specific vulnerabilities
report = skill.search(
    "Apache Struts remote code execution vulnerabilities 2024",
    depth="standard",
)

# Exposed API endpoints
report = skill.search(
    "find exposed swagger API docs on target.com",
    depth="deep",
)

# Git repository exposure
report = skill.search(
    "exposed .git directories on example.com",
    depth="deep",
)
```

**OSINT investigation — people**
```python
# By name
report = skill.search(
    'OSINT investigation on "John Doe" — social media, email, profiles',
    depth="deep",
)

# By email
report = skill.search(
    "investigate john.doe@example.com — find all accounts and mentions",
    depth="exhaustive",
)

# By username
report = skill.search(
    "find all accounts for username @johndoe42",
    depth="deep",
)

# By phone number
report = skill.search(
    "lookup phone number +1-555-123-4567",
    depth="standard",
)
```

**OSINT investigation — domains and companies**
```python
# Domain reconnaissance
report = skill.search(
    "full domain recon on target.com — subdomains, DNS, certificates, technology stack",
    depth="exhaustive",
)

# Company investigation
report = skill.search(
    'investigate company "Acme Corp" — employees, filings, data breaches',
    depth="deep",
)

# IP address lookup
report = skill.search(
    "investigate IP 192.168.1.1 — open ports, services, abuse reports",
    depth="standard",
)
```

**SEO analysis**
```python
# Site indexation check
report = skill.search(
    "SEO indexation analysis of example.com",
    depth="standard",
)

# Backlink research
report = skill.search(
    "find backlinks pointing to example.com",
    depth="deep",
)

# Competitor analysis
report = skill.search(
    "SEO competitor analysis for example.com — related sites, ranking keywords",
    depth="deep",
)

# Technical SEO audit
report = skill.search(
    "technical SEO check on example.com — sitemap, robots.txt, canonical, hreflang",
    depth="deep",
)
```

**Academic research**
```python
# Find papers
report = skill.search(
    "latest research papers on transformer architecture scaling laws 2024",
    depth="standard",
)

# Find datasets
report = skill.search(
    "download dataset for sentiment analysis benchmark CSV",
    depth="standard",
)

# Find authors and their work
report = skill.search(
    'research publications by author "Yann LeCun" on deep learning',
    depth="deep",
)
```

**Code and developer search**
```python
# Find repositories
report = skill.search(
    "python library for PDF text extraction with OCR support",
    depth="standard",
)

# Find packages
report = skill.search(
    "npm package for real-time WebSocket pub/sub",
    depth="standard",
)

# Debug errors
report = skill.search(
    "RuntimeError: CUDA out of memory pytorch solution",
    depth="standard",
)

# Find documentation
report = skill.search(
    "FastAPI dependency injection documentation examples",
    depth="quick",
)
```

**File hunting**
```python
# Find specific file types
report = skill.search(
    "machine learning cheat sheet filetype:pdf",
    depth="standard",
)

# Find datasets
report = skill.search(
    "US census data 2023 download CSV",
    depth="standard",
)

# Find configuration files
report = skill.search(
    "docker-compose example microservices filetype:yaml",
    depth="standard",
)
```

**News search**
```python
# Recent news
report = skill.search(
    "latest news on AI regulation this week",
    depth="standard",
)

# Breaking news
report = skill.search(
    "breaking news today cybersecurity",
    depth="quick",
)

# News analysis
report = skill.search(
    "analysis of EU AI Act implications for startups",
    depth="standard",
)
```

**Image and video search**
```python
# Images
report = skill.search(
    "high resolution photos of Mars surface NASA",
    depth="standard",
)

# Videos
report = skill.search(
    "video tutorial on Kubernetes deployment strategies",
    depth="standard",
)
```

**Social media search**
```python
# Reddit discussions
report = skill.search(
    "reddit discussion about best self-hosted alternatives to Google Photos",
    depth="standard",
)

# Forum threads
report = skill.search(
    "forum thread comparing Proxmox vs ESXi for home lab",
    depth="standard",
)
```

**Direct dork query (no intent parsing)**
```python
# Execute a raw dork you've written yourself
report = skill.search_dork(
    'site:github.com "API_KEY" filetype:env',
    engines=["google", "bing"],
)

print(report.to_context())
```

**Preview queries without executing them**
```python
# See what dork queries would be generated
dorks = skill.suggest_queries(
    "find SQL injection vulnerabilities on target.com"
)

for d in dorks:
    print(f"  Query: {d.query}")
    print(f"  Operators: {d.operators_used}")
    print(f"  Purpose: {d.purpose}")
    print()
```

**Build a custom dork from parameters**
```python
dork = skill.build_dork(
    keyword="confidential",
    domain="example.com",
    filetype="pdf",
    intitle="report",
    exclude=["public", "template"],
    exact_match=True,
)

print(f"Generated: {dork.query}")
# → site:example.com filetype:pdf intitle:"report" -public -template "confidential"

# Execute it
report = skill.search_dork(dork.query)
```

**Execute a named strategy against a target**
```python
# Full OSINT chain
report = skill.execute_strategy(
    strategy_name="osint_chain",
    target="suspect-domain.com",
    depth="exhaustive",
)

# Deep security dive
report = skill.execute_strategy(
    strategy_name="deep_dive",
    target="target.com",
    depth="deep",
)

# File hunting
report = skill.execute_strategy(
    strategy_name="file_hunt",
    target="example.com",
    depth="deep",
)

# Temporal trend analysis
report = skill.execute_strategy(
    strategy_name="temporal",
    target="AI regulation news",
    depth="deep",
)
```

**Batch search — multiple queries at once**
```python
queries = [
    "python FastAPI vs Flask performance",
    "rust web frameworks comparison 2024",
    "go gin framework documentation",
]

reports = skill.search_batch(queries, depth="quick")

for report in reports:
    print(f"Query: {report.query}")
    print(f"  Results: {len(report.results)}")
    print(f"  Best: {report.top(1)[0].title if report.results else 'None'}")
    print()
```

**Override engine and category selection**
```python
# Force specific engines
report = skill.search(
    "quantum computing breakthroughs",
    engines=["google_scholar", "arxiv", "semantic_scholar"],
)

# Force specific categories
report = skill.search(
    "kubernetes tutorial",
    categories=["it", "general"],
)

# Force time range
report = skill.search(
    "zero-day vulnerabilities",
    time_range="week",
)

# Force language
report = skill.search(
    "machine learning tutorials",
    language="en",
)
```

**Working with the SearchReport object**
```python
report = skill.search("advanced persistent threats 2024", depth="standard")

# LLM-ready text (for injecting into AI agent context)
context = report.to_context(max_results=20)

# Top N results sorted by relevance
top5 = report.top(5)

# Full result list
all_results = report.results

# What was detected
print(f"Intent: {report.intent.category.value}")        # e.g. "security"
print(f"Subcategory: {report.intent.subcategory}")       # e.g. "general"
print(f"Entities: {report.intent.entities}")             # e.g. {"year": "2024"}
print(f"Keywords: {report.intent.keywords}")             # e.g. ["advanced", "persistent", "threats"]
print(f"Confidence: {report.intent.confidence:.0%}")     # e.g. "80%"

# What strategy ran
print(f"Strategy: {report.strategy.name}")               # e.g. "multi_angle"
print(f"Steps: {len(report.strategy.steps)}")            # e.g. 2

# Performance metrics
print(f"Total found: {report.total_found}")              # before dedup
print(f"Final results: {len(report.results)}")           # after dedup+scoring
print(f"Time: {report.timing_seconds:.2f}s")
print(f"Engines used: {report.engines_used}")

# Suggested refinements
print(f"Suggestions: {report.suggestions}")

# Errors (if any)
print(f"Errors: {report.errors}")
```

**Working with individual SearchResult objects**
```python
for r in report.top(10):
    print(f"Title:     {r.title}")
    print(f"URL:       {r.url}")
    print(f"Snippet:   {r.snippet[:300]}")
    print(f"Relevance: {r.relevance:.2f} / 10.0")
    print(f"Engines:   {r.engines}")           # which SearXNG engines returned this
    print(f"Score:     {r.score}")              # raw SearXNG score
    print(f"Category:  {r.category}")           # SearXNG result category
    print(f"Positions: {r.positions}")          # rank positions across engines
    print(f"Metadata:  {r.metadata}")           # publishedDate, thumbnail, etc.
    print()
```

## AI Agent Integration

**Basic tool handler**
```python
from search_intelligence_skill import SearchSkill

skill = SearchSkill(searxng_url="http://localhost:8888")

def handle_search_tool(user_query: str) -> str:
    """Called by the AI agent when it needs to search the web."""
    report = skill.search(user_query, depth="standard")
    return report.to_context()
```

**With depth control from agent**
```python
def handle_search_tool(user_query: str, depth: str = "standard") -> str:
    report = skill.search(user_query, depth=depth)
    return report.to_context()
```

**Returning structured data to agent**
```python
def handle_search_tool(user_query: str) -> dict:
    report = skill.search(user_query, depth="standard")
    return {
        "query": report.query,
        "intent": f"{report.intent.category.value}/{report.intent.subcategory}",
        "confidence": report.intent.confidence,
        "result_count": len(report.results),
        "results": [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet[:500],
                "relevance": round(r.relevance, 2),
                "engines": r.engines,
            }
            for r in report.top(10)
        ],
        "suggestions": report.suggestions,
        "engines_used": report.engines_used,
        "time_seconds": round(report.timing_seconds, 2),
    }
```

**OpenAI function calling / tool definition**
```python
search_tool_schema = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the internet using advanced dork queries and multi-engine strategies. "
            "Supports security scanning, OSINT, SEO analysis, academic research, "
            "code search, file hunting, and general web search. "
            "Describe what you want to find in natural language."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query describing what to find",
                },
                "depth": {
                    "type": "string",
                    "enum": ["quick", "standard", "deep", "exhaustive"],
                    "description": "Search thoroughness: quick (1-2 queries), standard (3-6), deep (6-12), exhaustive (12+)",
                    "default": "standard",
                },
            },
            "required": ["query"],
        },
    },
}
```

**LangChain tool wrapper**
```python
from langchain.tools import Tool
from search_intelligence_skill import SearchSkill

skill = SearchSkill(searxng_url="http://localhost:8888")

search_tool = Tool(
    name="web_search",
    description=(
        "Advanced web search with dork generation and multi-engine strategies. "
        "Input a natural language query. Supports security, OSINT, SEO, academic, "
        "code, file, and general searches."
    ),
    func=lambda q: skill.search(q, depth="standard").to_context(),
)
```

**Context manager for clean resource handling**
```python
with SearchSkill(searxng_url="http://localhost:8888") as skill:
    report = skill.search("find open redirects on example.com")
    print(report.to_context())
# HTTP client is automatically closed
```

## Using Individual Components Directly

**IntentParser — analyze queries without searching**
```python
from search_intelligence_skill import IntentParser

parser = IntentParser()
intent = parser.parse("find exposed .env files on example.com")

print(f"Category:    {intent.category.value}")     # security
print(f"Subcategory: {intent.subcategory}")         # exposed_files
print(f"Entities:    {intent.entities}")            # {"domain": "example.com"}
print(f"Keywords:    {intent.keywords}")            # ["exposed", "env", "files"]
print(f"Depth:       {intent.depth.value}")         # standard
print(f"Time range:  {intent.time_range}")          # ""
print(f"Confidence:  {intent.confidence:.0%}")      # 95%
print(f"Constraints: {intent.constraints}")         # {}
```

**DorkGenerator — generate queries without searching**
```python
from search_intelligence_skill import DorkGenerator, IntentParser

parser = IntentParser()
gen = DorkGenerator()

intent = parser.parse("OSINT investigation on john@example.com")
dorks = gen.generate(intent)

for d in dorks:
    print(f"  [{', '.join(d.operators_used)}] {d.query}")
    print(f"  Purpose: {d.purpose}")

# Build a custom dork manually
custom = gen.generate_custom(
    keyword="secret",
    domain="example.com",
    filetype="env",
    intitle="config",
    exclude=["test", "demo"],
    exact_match=True,
)
print(f"Custom: {custom.query}")

# Translate a Google dork to Yandex syntax
yandex_dork = gen.translate(custom, target_engine="yandex")
print(f"Yandex: {yandex_dork.query}")

# Translate to Bing
bing_dork = gen.translate(custom, target_engine="bing")
print(f"Bing:   {bing_dork.query}")
```

**ResultAnalyzer — score and analyze results**
```python
from search_intelligence_skill import ResultAnalyzer, IntentParser, SearXNGClient

client = SearXNGClient(base_url="http://localhost:8888")
parser = IntentParser()
analyzer = ResultAnalyzer()

intent = parser.parse("python web frameworks comparison")

raw = client.search("python web frameworks comparison", engines=["google", "bing"])
results = client.parse_results(raw)

# Full analysis pipeline: deduplicate → score → sort
analyzed = analyzer.analyze(results, intent)

for r in analyzed[:5]:
    print(f"[{r.relevance:.2f}] {r.title}")

# Generate refinement suggestions
suggestions = analyzer.generate_refinements(analyzed, intent)
print(f"Suggestions: {suggestions}")

# Get a text summary
summary = analyzer.summarize(analyzed, intent)
print(summary)

client.close()
```

**SearXNGClient — direct API access**
```python
from search_intelligence_skill import SearXNGClient

client = SearXNGClient(base_url="http://localhost:8888")

# Single search
raw = client.search(
    query='site:github.com "fastapi" filetype:py',
    engines=["google", "bing", "duckduckgo"],
    categories=["general"],
    time_range="month",
    language="en",
    pageno=1,
    safesearch=0,
)

# Parse results into SearchResult objects
results = client.parse_results(raw)

# Get SearXNG suggestions
suggestions = client.get_suggestions(raw)

# Get spelling corrections
corrections = client.get_corrections(raw)

# See which engines failed
unresponsive = client.get_unresponsive(raw)

# Batch search
responses = client.search_batch(
    queries=["query 1", "query 2", "query 3"],
    engines=["google"],
)

# Health check
if client.health_check():
    print("SearXNG is online")

client.close()
```

## Quick Reference

**Search Depths**
```python
from search_intelligence_skill import Depth

Depth.QUICK        # 1-2 queries, single step, fast lookups
Depth.STANDARD     # 3-6 queries, multi-engine, general searching
Depth.DEEP         # 6-12 queries, multi-step, thorough research
Depth.EXHAUSTIVE   # 12+ queries, full sweep, complete investigations
```

**Intent Categories (auto-detected)**
```python
from search_intelligence_skill import IntentCategory

IntentCategory.GENERAL    # General web search
IntentCategory.SECURITY   # Vulnerabilities, exposed files, pentesting
IntentCategory.SEO        # Indexation, backlinks, competitors, technical SEO
IntentCategory.OSINT      # People, emails, usernames, domains, companies
IntentCategory.ACADEMIC   # Papers, datasets, authors, journals
IntentCategory.CODE       # Repositories, packages, docs, bugs
IntentCategory.FILES      # Documents, data files, archives, media
IntentCategory.NEWS       # Breaking news, analysis, trends
IntentCategory.IMAGES     # Image search
IntentCategory.VIDEOS     # Video search
IntentCategory.SOCIAL     # Reddit, forums, discussions
IntentCategory.SHOPPING   # Products, prices, comparisons
IntentCategory.LEGAL      # Law, regulations, patents
IntentCategory.MEDICAL    # Health, diseases, clinical research
```

**Search Strategies (auto-selected by depth + intent)**
```python
# Strategies are selected automatically, but you can also invoke them directly:
skill.execute_strategy("quick", target="example.com")           # 1 step, top engines
skill.execute_strategy("broad_to_narrow", target="example.com") # Wide then focused
skill.execute_strategy("multi_angle", target="example.com")     # Same topic, different formulations
skill.execute_strategy("deep_dive", target="example.com")       # Exhaustive dork coverage
skill.execute_strategy("osint_chain", target="example.com")     # Progressive recon
skill.execute_strategy("verify", target="some claim")           # Cross-reference sources
skill.execute_strategy("file_hunt", target="example.com")       # Targeted file search
skill.execute_strategy("temporal", target="AI news")            # Across time periods
```

**Supported SearXNG Engines (90+)**
```python
# General: google, bing, duckduckgo, brave, qwant, startpage, mojeek,
#          yandex, yahoo, presearch, wiby, stract, yep, baidu, naver ...
#
# IT/Dev:  github, stackoverflow, gitlab, npm, pypi, dockerhub,
#          arch_linux_wiki, crates_io, packagist, pkg_go_dev ...
#
# Science: arxiv, google_scholar, semantic_scholar, crossref, pubmed,
#          base, openalex, core, wolfram_alpha ...
#
# News:    google_news, bing_news, yahoo_news, brave_news, wikinews ...
#
# Social:  reddit, lemmy, mastodon, hacker_news, lobsters ...
#
# Images:  google_images, bing_images, flickr, unsplash, openverse ...
#
# Videos:  youtube, google_videos, dailymotion, vimeo, piped, odysee ...
#
# Files:   piratebay, 1337x, annas_archive, z_library ...
#
# Music:   bandcamp, genius, soundcloud, youtube_music ...
#
# Maps:    openstreetmap, photon ...
#
# Wikis:   wikipedia, wikidata, wikimedia_commons ...
```

**Dork Operators (auto-translated across engines)**
```python
# Google operators:
#   site:  filetype:  intitle:  allintitle:  inurl:  allinurl:
#   intext:  allintext:  inanchor:  cache:  related:  info:  define:
#   before:  after:  AROUND(N)  "exact"  -exclude  OR  *  N..M
#
# Bing operators:
#   site:  filetype:  intitle:  inurl:  inbody:  contains:  ip:
#   language:  loc:  prefer:  feed:  "exact"  -exclude  OR  NEAR:N
#
# DuckDuckGo operators:
#   site:  filetype:  intitle:  inurl:  "exact"  -exclude  OR
#
# Yandex operators:
#   site:  mime:  title:  inurl:  host:  domain:  lang:  date:
#   "exact"  -exclude  |
#
# Brave operators:
#   site:  filetype:  intitle:  inurl:  "exact"  -exclude  OR
#
# The skill auto-translates between engines:
#   filetype: → mime: (Yandex)
#   intitle:  → title: (Yandex)
#   intext:   → inbody: (Bing)
```

## Dork Template Library

**Security dorks available (by subcategory)**
```
exposed_files      — .env, .log, .sql, .bak, .conf, .pem, .key, .json
directory_listing  — "index of", "directory listing", "parent directory"
admin_panels       — /admin, /login, /dashboard, wp-admin, phpmyadmin, cpanel
sensitive_data     — passwords, RSA keys, AWS keys, database URLs, SMTP creds
exposed_apis       — /api/, swagger, api-docs, graphql, openapi
subdomains         — site:*.domain, external references, inurl:domain
git_exposed        — .git, .git/config, .svn, .hg
technology_stack   — "powered by", wp-content, X-Powered-By
general            — CVE, exploit, PoC, security advisory
```

**OSINT dorks available (by subcategory)**
```
person    — LinkedIn, Twitter/X, Facebook, Instagram, GitHub, Medium, resume, CV
email     — email mentions, cross-site, leaks, LinkedIn, GitHub
username  — GitHub, Reddit, Twitter, Instagram, YouTube, Keybase, StackOverflow
domain    — site:, subdomains, whois, Shodan, DNS, SSL, Censys, crt.sh
company   — LinkedIn company, Crunchbase, Glassdoor, SEC filings, employees
phone     — whitepages, truecaller, Facebook, name/address
ip        — Shodan, abuse/blacklist, open ports, whois
```

**SEO dorks available (by subcategory)**
```
indexation     — site:, sitemap, blog, tag/category pages
backlinks      — external mentions, anchor text, link:
competitors    — related:, same-keyword competitors
content_audit  — intitle/inurl/intext keyword matching
technical_seo  — sitemap XML, robots.txt, noindex, canonical, hreflang, schema
```

**Academic dorks available (by subcategory)**
```
papers   — arxiv, ResearchGate, academia.edu, DOI, .edu PDFs
datasets — CSV, JSON, Kaggle, HuggingFace, Zenodo
authors  — Google Scholar, ORCID, ResearchGate, publication lists
```

**Code dorks available (by subcategory)**
```
repositories  — GitHub, GitLab, Bitbucket, Codeberg, Sourcehut
packages      — npm, PyPI, crates.io, RubyGems, Packagist, pkg.go.dev
documentation — ReadTheDocs, README, API references
issues_bugs   — GitHub issues, StackOverflow errors
```

## Advanced Usage

**Cross-engine dork translation**
```python
from search_intelligence_skill import DorkGenerator

gen = DorkGenerator()

# Build a Google dork
dork = gen.generate_custom(
    keyword="secret",
    domain="example.com",
    filetype="env",
    intitle="config",
)
print(f"Google: {dork.query}")
# → site:example.com filetype:env intitle:"config" secret

# Translate to Yandex (filetype → mime, intitle → title)
yandex = gen.translate(dork, "yandex")
print(f"Yandex: {yandex.query}")
# → site:example.com mime:env title:"config" secret

# Translate to Bing
bing = gen.translate(dork, "bing")
print(f"Bing:   {bing.query}")

# Translate to DuckDuckGo (drops unsupported operators)
ddg = gen.translate(dork, "duckduckgo")
print(f"DDG:    {ddg.query}")

# Translate to an engine without operator support (strips all operators)
plain = gen.translate(dork, "wikipedia")
print(f"Plain:  {plain.query}")
```

**Result scoring details**
```python
# Each result is scored on 7 signals (0-10 scale):
#
# 1. SearXNG base score (normalized)        — weight: 2.0
# 2. Keyword match in title + snippet       — weight: 3.0
# 3. Multi-engine agreement (appeared in N)  — weight: 0.5/engine, max 2.0
# 4. Position rank (lower = better)          — weight: 1.5
# 5. Source credibility (.gov +1.5, .edu +1.4, arxiv +1.4, etc.)
# 6. Content quality (snippet length, HTTPS, URL sanity)
# 7. Intent-specific boost (arxiv for academic, github for code, etc.)
#
# Credibility penalties: spam (-0.7), "click here" (-0.5), "free download" (-0.4)
```

**Auto-refinement behavior**
```python
# When auto_refine=True (default) and results < 5:
# 1. Analyzer generates refined queries (broader, different keywords)
# 2. Skill executes up to 3 refinement queries
# 3. New results are merged with originals
# 4. Full dedup + re-scoring runs
# 5. Process repeats up to max_refine_rounds

skill = SearchSkill(
    searxng_url="http://localhost:8888",
    auto_refine=True,
    max_refine_rounds=2,  # Try refining up to 2 times
)

# Disable auto-refinement for speed-critical paths
skill_fast = SearchSkill(
    searxng_url="http://localhost:8888",
    auto_refine=False,
)
```

**Entity extraction capabilities**
```python
from search_intelligence_skill import IntentParser

parser = IntentParser()

# Domains
intent = parser.parse("scan example.com for vulnerabilities")
# entities: {"domain": "example.com"}

# Emails
intent = parser.parse("investigate user@company.com")
# entities: {"email": "user@company.com", "email_domain": "company.com"}

# IPs
intent = parser.parse("lookup 192.168.1.1")
# entities: {"ip": "192.168.1.1"}

# CVEs
intent = parser.parse("details on CVE-2024-3094")
# entities: {"cve": "CVE-2024-3094"}

# Phone numbers
intent = parser.parse("find owner of +1-555-123-4567")
# entities: {"phone": "+1-555-123-4567"}

# Usernames
intent = parser.parse("find accounts for @johndoe42")
# entities: {"username": "johndoe42"}

# Names (quoted)
intent = parser.parse('investigate "John Smith"')
# entities: {"name": "John Smith"}

# Names (capitalized pattern)
intent = parser.parse("find information about Jane Doe")
# entities: {"name": "Jane Doe"}

# File types
intent = parser.parse("find documents filetype:pdf")
# entities: {"filetype": "pdf"}

# Years
intent = parser.parse("research papers from 2024")
# entities: {"year": "2024"}

# Multiple entities combined
intent = parser.parse('CVE-2024-3094 on example.com "John Doe"')
# entities: {"cve": "CVE-2024-3094", "domain": "example.com", "name": "John Doe"}
```

**Time range detection**
```python
from search_intelligence_skill import IntentParser

parser = IntentParser()

parser.parse("news today").time_range                  # "day"
parser.parse("what happened this week").time_range     # "week"
parser.parse("articles from last month").time_range    # "month"
parser.parse("publications this year").time_range      # "year"
parser.parse("latest updates on AI").time_range        # "month" (heuristic)
parser.parse("history of computing").time_range        # "" (no time constraint)
```

**Constraint extraction**
```python
from search_intelligence_skill import IntentParser

parser = IntentParser()

# Language constraints
intent = parser.parse("machine learning tutorials in spanish")
# constraints: {"language": "es"}

# Exhaustive hints
intent = parser.parse("find everything about this vulnerability")
# constraints: {"exhaustive": True}

# Result limits
intent = parser.parse("top 20 python frameworks")
# constraints: {"limit": 20}

# Exclusion hints
intent = parser.parse("web frameworks except Django without Flask")
# constraints: {"exclude": ["django", "flask"]}
```

**Pagination**
```python
from search_intelligence_skill import SearXNGClient

client = SearXNGClient(base_url="http://localhost:8888")

# Fetch multiple pages
all_results = []
for page in range(1, 4):
    raw = client.search("python frameworks", pageno=page)
    results = client.parse_results(raw)
    all_results.extend(results)
    if not results:
        break

print(f"Total across 3 pages: {len(all_results)}")
client.close()
```

**Rate limiting and retries**
```python
# Built-in rate limiting between requests
skill = SearchSkill(
    searxng_url="http://localhost:8888",
    rate_limit=1.0,    # 1 second minimum between requests
    max_retries=3,     # Retry failed requests up to 3 times
    timeout=30.0,      # 30 second timeout per request
)

# Rate limiting is automatic — no manual sleep() needed
# Retries use increasing delays on 429 (Too Many Requests)
```

**Logging for debugging**
```python
import logging

# See everything the skill does
logging.basicConfig(level=logging.DEBUG)

# Or just info-level
logging.basicConfig(level=logging.INFO)

skill = SearchSkill(searxng_url="http://localhost:8888")
report = skill.search("test query", depth="standard")

# Logs will show:
# INFO — Intent: security/exposed_files (confidence=0.95) — entities: {"domain": "..."}
# INFO — Strategy: multi_angle — 2 steps
# DEBUG — Executing step 1: Search angle 1
# DEBUG — Search 'site:... filetype:env' returned 12 results
# DEBUG — Executing step 2: Search angle 2
# INFO — Search complete: 23 results, 4.21s, 4 engines
```

## API Methods

| Method | Purpose | Returns |
|---|---|---|
| `skill.search(query, depth, ...)` | Full intelligent search pipeline | `SearchReport` |
| `skill.search_dork(dork, ...)` | Execute raw dork query directly | `SearchReport` |
| `skill.suggest_queries(query)` | Preview dorks without executing | `list[DorkQuery]` |
| `skill.build_dork(keyword, ...)` | Build custom dork from parameters | `DorkQuery` |
| `skill.execute_strategy(name, target)` | Run named strategy against target | `SearchReport` |
| `skill.search_batch(queries, ...)` | Execute multiple searches | `list[SearchReport]` |
| `skill.health_check()` | Check SearXNG connectivity | `bool` |
| `skill.close()` | Close HTTP client | `None` |

## SearchReport Properties

| Property | Type | Description |
|---|---|---|
| `.query` | `str` | Original natural language query |
| `.intent` | `SearchIntent` | Parsed intent with category, entities, keywords |
| `.strategy` | `SearchStrategy` | Strategy that was used (name, steps) |
| `.results` | `list[SearchResult]` | Scored and deduplicated results |
| `.total_found` | `int` | Total results before deduplication |
| `.suggestions` | `list[str]` | Refinement suggestions |
| `.refined_queries` | `list[str]` | Auto-refinement queries used |
| `.errors` | `list[str]` | Errors encountered during search |
| `.timing_seconds` | `float` | Total wall-clock time |
| `.engines_used` | `list[str]` | Engines that returned results |
| `.to_context(max_results)` | `str` | LLM-formatted text output |
| `.top(n)` | `list[SearchResult]` | Top N by relevance score |

## SearchResult Properties

| Property | Type | Description |
|---|---|---|
| `.title` | `str` | Result title |
| `.url` | `str` | Result URL |
| `.snippet` | `str` | Content snippet / description |
| `.engines` | `list[str]` | Which SearXNG engines returned it |
| `.score` | `float` | Raw SearXNG score |
| `.relevance` | `float` | Computed multi-signal relevance (0-10) |
| `.category` | `str` | SearXNG result category |
| `.positions` | `list[int]` | Rank positions across engines |
| `.metadata` | `dict` | Extra fields: publishedDate, thumbnail, img_src |

## Troubleshooting

**SearXNG not reachable**
```bash
# Check the instance is running
curl http://localhost:8888/healthz

# Check JSON API is enabled
curl "http://localhost:8888/search?q=test&format=json"

# Common fixes:
# 1. Ensure port mapping is correct (docker: -p 8888:8080)
# 2. Ensure search.formats includes "json" in settings.yml
# 3. Check firewall rules
```

```python
if not skill.health_check():
    print("SearXNG unreachable — check URL, port, and settings")
```

**No results returned**
```python
report = skill.search("very specific obscure query")

if not report.results:
    print("No results. Try:")
    print("  1. Broader keywords")
    print("  2. Different depth: depth='deep'")
    print("  3. Check suggestions:", report.suggestions)
    print("  4. Check errors:", report.errors)
    print("  5. Try different engines:", report.engines_used)

    # Manual broader search
    report2 = skill.search("broader version of query", depth="deep")
```

**Timeout errors**
```python
# Increase timeout for complex queries
skill = SearchSkill(
    searxng_url="http://localhost:8888",
    timeout=60.0,      # 60 seconds
    max_retries=3,     # More retries
)
```

**Rate limiting (429 errors)**
```python
# Increase delay between requests
skill = SearchSkill(
    searxng_url="http://localhost:8888",
    rate_limit=2.0,    # 2 seconds between requests
)
```

**SSL errors (local development only)**
```python
skill = SearchSkill(
    searxng_url="https://localhost:8888",
    verify_ssl=False,  # ONLY for local dev — never in production
)
```

**Wrong intent detected**
```python
# If the auto-detection picks the wrong category, use direct dork:
report = skill.search_dork(
    'site:example.com filetype:pdf "annual report"',
    engines=["google", "bing"],
)

# Or force engines/categories:
report = skill.search(
    "some ambiguous query",
    engines=["google_scholar", "arxiv"],
    categories=["science"],
)
```

**Memory usage with large result sets**
```python
# Limit results to control memory
report = skill.search("broad query", depth="exhaustive", max_results=50)

# Process results in a streaming fashion
for r in report.results:
    process(r)  # handle one at a time
```

## How It All Works Together

```
User Query
    │
    ▼
┌─────────────────┐
│  IntentParser    │──→ category, subcategory, entities, keywords
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DorkGenerator   │──→ 5-20 optimized dork queries with operators
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ StrategyPlanner  │──→ multi-step plan (which dorks, which engines, what order)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SearXNGClient   │──→ executes queries against your instance (retries, rate limit)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ResultAnalyzer   │──→ dedup, score, rank, credibility check
└────────┬────────┘
         │
    (if results poor)
         │
         ▼
┌─────────────────┐
│  Auto-Refine     │──→ generate new queries, re-search, re-analyze
└────────┬────────┘
         │
         ▼
   SearchReport
  .to_context() → LLM-ready text
  .top(n) → best results
  .results → full list
```

## Notes

**Privacy**
- All searches route through YOUR SearXNG instance
- Zero API keys required for any engine
- No data sent to third-party services (except through SearXNG's engine requests)
- SearXNG strips tracking parameters and anonymizes requests

**Performance tips**
- Reuse the `SearchSkill` instance across searches (connection pooling)
- Use `depth="quick"` for simple lookups, reserve `"deep"` / `"exhaustive"` for research
- Set `auto_refine=False` for speed-critical paths
- Use `skill.suggest_queries()` to preview before executing expensive searches
- Batch independent queries with `skill.search_batch()`

**Accuracy tips**
- Include specific entities in your query (domains, emails, CVEs, names)
- Use quoted phrases for exact matching: `'find "exact phrase"'`
- Specify time ranges when freshness matters: `"latest news this week"`
- Use `depth="deep"` or `"exhaustive"` for comprehensive coverage
- Check `report.suggestions` for refinement ideas
- Check `report.intent` to verify the skill understood your query correctly

**Extending the skill**
- Add new dork templates in `config.py` → `DORK_TEMPLATES`
- Add new intent signals in `config.py` → `INTENT_SIGNALS`
- Add new engines in `config.py` → `ENGINE_CATEGORIES`
- Add new operator translations in `config.py` → `OPERATOR_SUPPORT`
- Add new strategies in `config.py` → `STRATEGY_DEFINITIONS`
- Add new subcategory detection in `intent.py` → `SUBCATEGORY_PATTERNS`

**Confirm before sensitive operations**
- Security scanning dorks may trigger alerts on target domains
- OSINT queries may involve personal information — use responsibly
- Always validate that the target domain/entity is authorized for testing
- This tool is for legitimate research, authorized security testing, and SEO analysis
