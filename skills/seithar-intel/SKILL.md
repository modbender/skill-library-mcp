---
name: seithar-intel — Threat Intelligence & Cognitive Security Feed
description: A personal cyber threat intelligence and cognitive security analyst
  for OpenClaw. Monitors RSS feeds for security news, vulnerability disclosures,
  exploit drops, and influence operation reports. Sc...
---

# seithar-intel — Threat Intelligence & Cognitive Security Feed

## Seithar Group — Intelligence Division
## 認知作戦 | seithar.com

A personal cyber threat intelligence and cognitive security analyst for OpenClaw. Monitors RSS feeds for security news, vulnerability disclosures, exploit drops, and influence operation reports. Scores items against your interests, delivers daily briefings, and provides on-demand deep-dive analysis of any threat — technical or cognitive.

This is ThreatMouth in your pocket. Cyber + cognitive security awareness from any chat app.

---

## Description

This skill turns your OpenClaw into a threat intelligence analyst that:

- Monitors cybersecurity RSS feeds (BleepingComputer, The Hacker News, Krebs on Security, CISA, Full Disclosure, Exploit-DB, SANS ISC, oss-security, Schneier, PacketStorm, DarkReading, and more)
- Monitors cognitive security feeds (EUvsDisinfo, DFRLab, Bellingcat, RAND, Seithar Research)
- Scores each item against your configured interest profile
- Delivers morning/evening briefings via your preferred chat app
- Provides on-demand deep-dive analysis of any CVE, vulnerability, exploit, influence operation, or campaign
- Tracks MITRE ATT&CK and DISARM framework technique mappings
- Discovers public proof-of-concept code for disclosed vulnerabilities
- Maintains a running threat landscape summary that evolves with the feed

---

## Triggers

- "threat briefing" / "security briefing" / "morning briefing" / "what's new in security"
- "check threats" / "check feeds" / "any new vulns"
- "explain CVE-XXXX-XXXXX" / "deep dive on [topic]" / "analyze this threat"
- "cogdef briefing" / "cognitive security update" / "any new psyops"
- "what should I study today" / "learning recommendations"
- "threat landscape" / "what's trending in security"
- "poc for CVE-XXXX-XXXXX" / "any exploits for [software]"
- "seithar brief"

---

## Configuration

The operator should configure the following in their OpenClaw settings or by telling the agent directly:

### Interest Profile

Tell your OpenClaw your security interests and it will calibrate scoring. Example:

```
My security interests are:
- Malware analysis and reverse engineering
- Social engineering and cognitive security
- Network exploitation
- OSINT and intelligence gathering
- Influence operations and information warfare
- Vulnerability research and exploit development

I'm currently studying:
- MITRE ATT&CK framework
- DISARM framework for influence operations
- Python security tooling
- OverTheWire wargames

My skill level: intermediate

Deprioritize:
- Enterprise compliance and GRC
- Cloud IAM and AWS security
- Vendor marketing announcements
- Corporate breach notifications unless technically interesting
```

The skill stores this profile in memory and uses it to score every feed item for relevance.

### Feed Schedule

Default schedule (configurable):
- **Morning briefing**: 8:00 AM local — top 5 items from overnight, any critical alerts
- **Evening briefing**: 6:00 PM local — day summary, items scored > 0.7, study recommendations
- **Critical alerts**: Immediate — items scored > 0.9 pushed as soon as detected

Tell your OpenClaw: "Change my briefing time to 9 AM and 7 PM" or "Only send critical alerts, no scheduled briefings"

### Feed Check Interval

Default: every 2 hours. The skill uses OpenClaw's cron/heartbeat system to periodically fetch and process feeds.

---

## How It Works

### Feed Collection

On each check interval, the skill instructs the agent to:

1. Fetch RSS feeds from the configured source list using the `web_fetch` tool
2. Parse feed entries (title, link, published date, summary/description)
3. Deduplicate against previously seen items (tracked in memory by URL hash)
4. For each new item, score it against the operator's interest profile

### Scoring

Each new item is scored 0.0 to 1.0 against the operator's profile:

- **0.9 - 1.0**: Critical — matches core interests directly, high urgency (active exploitation, 0-day, major campaign)
- **0.7 - 0.9**: High — relevant to interests, worth reading today
- **0.5 - 0.7**: Medium — tangentially relevant, include in digest
- **Below 0.5**: Low — skip unless specifically requested

The agent scores by examining the item's title, summary, source, and any CVE/technique references against the stored interest profile. No external API needed — the LLM does the scoring inline.

### Categorization

Items are categorized into:

- **CRITICAL ALERT** — Active exploitation, 0-day, critical infrastructure
- **EXPLOIT DROP** — New CVE, PoC release, vulnerability disclosure
- **MALWARE** — Malware analysis, RE findings, campaign reports
- **INFLUENCE OP** — Disinformation campaigns, cognitive security, DISARM-mapped operations
- **TECHNIQUE** — ATT&CK or DISARM technique deep-dives, methodology
- **LEARNING** — Tutorials, CTF writeups, educational content
- **GENERAL** — Industry news, policy, commentary

### Briefing Format

```
╔══════════════════════════════════════════════════╗
║  SEITHAR INTELLIGENCE BRIEFING                   ║
║  2026-02-11 08:00 EST                            ║
╚══════════════════════════════════════════════════╝

CRITICAL (act now):

  🔴 [0.95] Pre-auth RCE in OpenSSH (CVE-2026-XXXXX)
     Full Disclosure | 2h ago
     Affects OpenSSH 9.x. Public PoC available.
     ▸ Say "deep dive CVE-2026-XXXXX" for full analysis

HIGH RELEVANCE:

  🟠 [0.87] Lazarus Group deploys new social engineering
     toolkit targeting crypto developers
     The Hacker News | 4h ago
     DISARM: T0047 (Develop Content), ATT&CK: T1566.001
     ▸ Say "deep dive lazarus social engineering" for analysis

  🟠 [0.82] New Nuclei templates for Spring4Shell variants
     Exploit-DB | 6h ago
     12 new detection templates + PoC payloads
     ▸ Say "explain spring4shell" for context

  🟠 [0.78] Russian influence operation targeting NATO
     narratives detected across 3 platforms
     DFRLab | 5h ago
     DISARM: T0046, T0048, T0056 | Coordinated inauthentic behavior
     ▸ Say "deep dive nato influence op" for DISARM breakdown

STUDY RECOMMENDATION:
  Based on today's feed: review SSH key exchange internals
  and pre-authentication attack surfaces. OverTheWire Bandit
  levels 14-17 cover SSH fundamentals.

──────────────────────────────────────────────────
24 items collected | 4 high relevance | 1 critical
Seithar Intelligence Division v1.0
認知作戦 | seithar.com/research
──────────────────────────────────────────────────
```

### Deep Dive

When the operator says "deep dive [topic]" or "explain [CVE]", the skill:

1. Fetches the full article content via `web_fetch`
2. If a CVE is mentioned, queries the NVD API for structured vuln data
3. Searches GitHub for public PoC repositories (`https://api.github.com/search/repositories?q=CVE-XXXX-XXXXX&sort=stars`)
4. Generates a structured educational breakdown:

```
╔══════════════════════════════════════════════════╗
║  SEITHAR DEEP DIVE                               ║
║  CVE-2026-XXXXX — OpenSSH Pre-Auth RCE           ║
╚══════════════════════════════════════════════════╝

WHAT HAPPENED:
  A memory corruption vulnerability in OpenSSH's key exchange
  handler allows unauthenticated attackers to achieve remote
  code execution as root. No credentials required.

HOW THE EXPLOIT WORKS:
  1. Attacker connects to SSH port 22
  2. During key exchange (before authentication), sends
     oversized payload in the KEX_INIT message
  3. Buffer overflow overwrites return address on stack
  4. Execution redirected to attacker's shellcode
  5. Root shell achieved — no credentials needed

  Pseudocode:
    connect(target, 22)
    send(kex_init_with_overflow_payload)
    # Stack is now corrupted
    # Return address points to shellcode
    # Root shell spawns

MITRE ATT&CK:
  T1190 — Exploit Public-Facing Application
  T1068 — Exploitation for Privilege Escalation

PROOF OF CONCEPT:
  ⭐ 234  github.com/researcher/CVE-2026-XXXXX (Python)
  ⭐  45  github.com/other/openssh-rce-poc (C)
  Key file to study: exploit.py lines 40-80 (payload construction)

CONCEPTS TO UNDERSTAND:
  → Stack-based buffer overflow (study: OverTheWire Narnia)
  → SSH key exchange protocol (RFC 4253)
  → ASLR bypass techniques
  → Return-oriented programming (ROP)

LAB EXERCISE:
  docker pull vulhub/openssh:9.x
  Practice in isolated environment. Never test against
  production systems.

DEFENSIVE PERSPECTIVE:
  Detection: Anomalous packet sizes during SSH handshake
  Prevention: Upgrade to OpenSSH 9.x.x, restrict SSH access
  Log analysis: Look for connection resets during KEX phase

──────────────────────────────────────────────────
Seithar Intelligence Division v1.0
認知作戦 | seithar.com/research
──────────────────────────────────────────────────
```

For influence operations, the deep dive maps to DISARM instead:

```
╔══════════════════════════════════════════════════╗
║  SEITHAR DEEP DIVE — COGNITIVE                   ║
║  Russian NATO Narrative Operation                 ║
╚══════════════════════════════════════════════════╝

WHAT HAPPENED:
  Coordinated inauthentic behavior detected across Twitter/X,
  Telegram, and Facebook targeting NATO unity narratives in
  Baltic states. ~200 accounts activated within 48h window.

DISARM MAPPING:
  Plan:
    T0073 — Determine Target Audiences (Baltic publics)
    T0047 — Develop Content (localized memes, fake news articles)
  Prepare:
    T0048 — Develop Online Personas (aged accounts reactivated)
    T0046 — Use Existing Narratives (energy costs, immigration)
  Execute:
    T0049 — Flood Information Space
    T0056 — Amplify Existing Content (cross-platform coordination)

TECHNIQUES DETECTED:
  ▸ Narrative Piggybacking — latched onto real energy cost
    concerns, added fabricated escalation claims
  ▸ Coordinated Amplification — same framing appeared across
    platforms within 2-hour window, suggesting central dispatch
  ▸ Emotional Anchoring — content led with fear/anger triggers
    before introducing anti-NATO framing

SEITHAR TAXONOMY:
  SCT-003 (Substrate Priming) — Initial wave didn't carry
    explicit anti-NATO messaging. It primed emotional state
    (anxiety about energy costs) so subsequent waves could
    introduce the geopolitical framing.
  SCT-005 (Amplification Embedding) — Content designed so
    that debunking it still spreads the core claim.
  SCT-007 (Wetiko Pattern) — Target audiences began
    reproducing the framing as "their own analysis" within
    48h of initial exposure.

DEFENSIVE PERSPECTIVE:
  Inoculation: Pre-bunking energy cost narratives with
  accurate data before the operation gains traction.
  Detection: Monitor for coordinated posting patterns
  (same framing, multiple accounts, tight time window).
  Counter: Highlight the coordination pattern itself rather
  than debunking individual claims.

──────────────────────────────────────────────────
Seithar Intelligence Division v1.0
認知作戦 | seithar.com/research
──────────────────────────────────────────────────
```

---

## RSS Feed Sources

### Cyber Threat Intelligence (Tier 1 — checked every 2h)

| Source | Feed URL | Category |
|--------|----------|----------|
| The Hacker News | https://feeds.feedburner.com/TheHackersNews | general, malware, exploit |
| BleepingComputer | https://www.bleepingcomputer.com/feed/ | general, malware |
| Krebs on Security | https://krebsonsecurity.com/feed/ | general, cybercrime |
| CISA Alerts | https://www.cisa.gov/cybersecurity-advisories/all.xml | critical, advisory |
| Full Disclosure | https://seclists.org/rss/fulldisclosure.rss | exploit, disclosure |
| oss-security | https://seclists.org/rss/oss-sec.rss | exploit, disclosure |
| Exploit-DB | https://www.exploit-db.com/rss.xml | exploit, poc |
| SANS ISC | https://isc.sans.edu/rssfeed.xml | general, technique |
| PacketStorm | https://packetstormsecurity.com/feeds/headlines.xml | exploit, tools |
| Schneier on Security | https://www.schneier.com/feed/ | commentary, crypto |
| Dark Reading | https://www.darkreading.com/rss.xml | general, enterprise |

### Cognitive Security (Tier 1 — checked every 4h)

| Source | Feed URL | Category |
|--------|----------|----------|
| EUvsDisinfo | https://euvsdisinfo.eu/feed/ | influence_op, disinfo |
| Bellingcat | https://www.bellingcat.com/feed/ | osint, investigation |
| DFRLab (Atlantic Council) | https://www.atlanticcouncil.org/category/digital-forensic-research-lab/feed/ | influence_op, analysis |
| RAND Cyber/Info | https://www.rand.org/topics/cyber-and-data-sciences.xml | research, policy |
| Recorded Future (Insikt) | https://www.recordedfuture.com/feed | threat_intel, apt |

### Niche / Learning (Tier 2 — checked every 6h)

| Source | Feed URL | Category |
|--------|----------|----------|
| r/netsec | https://www.reddit.com/r/netsec/.rss | community, technique |
| r/ReverseEngineering | https://www.reddit.com/r/ReverseEngineering/.rss | re, technique |
| Project Zero | https://googleprojectzero.blogspot.com/feeds/posts/default | research, exploit |
| Malwarebytes Labs | https://www.malwarebytes.com/blog/feed | malware, consumer |
| Troy Hunt | https://www.troyhunt.com/rss/ | general, web_security |
| Graham Cluley | https://grahamcluley.com/feed/ | general, commentary |
| Risky Business | https://risky.biz/feeds/risky-business/ | podcast, commentary |

The operator can add or remove sources by telling the agent: "Add this RSS feed to my threat sources: [url]" or "Remove Dark Reading from my feeds."

---

## Memory Structure

The skill uses OpenClaw's persistent memory to track:

```json
{
  "seithar_intel": {
    "profile": {
      "interests": ["malware analysis", "social engineering", "network exploitation"],
      "skill_level": "intermediate",
      "currently_studying": ["MITRE ATT&CK", "DISARM", "OverTheWire"],
      "deprioritize": ["enterprise compliance", "cloud IAM"]
    },
    "feeds": {
      "sources": ["list of active RSS URLs"],
      "custom_sources": ["user-added URLs"],
      "check_interval_hours": 2,
      "briefing_times": ["08:00", "18:00"]
    },
    "seen_items": {
      "url_hashes": ["hash1", "hash2"],
      "last_check": "2026-02-11T14:00:00Z",
      "items_today": 24,
      "high_relevance_today": 4
    },
    "stats": {
      "total_items_processed": 1847,
      "deep_dives_requested": 23,
      "top_sources_by_relevance": {
        "fulldisclosure": 0.82,
        "exploit_db": 0.79,
        "euvsdisinfo": 0.76
      },
      "most_seen_techniques": {
        "T1566.001": 12,
        "T0049": 8,
        "T1190": 7
      }
    },
    "study_log": {
      "deep_dives_completed": ["CVE-2026-XXXXX", "lazarus_social_engineering"],
      "techniques_studied": ["T1190", "T0049", "SCT-003"],
      "recommended_next": "SSH key exchange internals"
    }
  }
}
```

---

## Proactive Behavior

Using OpenClaw's heartbeat/cron system, the skill proactively:

1. **Checks feeds** on the configured interval without being asked
2. **Pushes critical alerts** immediately when items score > 0.9
3. **Sends scheduled briefings** at configured times
4. **Tracks study progress** — if the operator does a deep dive on a topic, related items in future feeds are boosted in scoring
5. **Notices patterns** — if multiple sources report on the same CVE or campaign within 24h, it flags convergence: "Multiple sources reporting on CVE-XXXX-XXXXX. This is gaining traction — consider prioritizing."
6. **Weekly summary** — every Sunday, a summary of the week's threat landscape: top CVEs, active campaigns, technique trends, and study recommendations for the coming week

---

## Skill Files

### SKILL.md (this file)

The agent reads this and knows how to operate. No external code needed — OpenClaw's built-in `web_fetch`, `web_search`, memory, and cron tools handle everything.

### sources.md

List of RSS feed URLs with categories and check intervals. The agent reads this file when performing feed checks.

### frameworks/disarm-techniques.md

Reference list of DISARM techniques with IDs, names, and one-line descriptions. The agent uses this to map influence operations to framework codes.

### frameworks/attack-techniques.md

Reference list of MITRE ATT&CK techniques (top 50 most relevant). Used for technique mapping in deep dives.

### frameworks/seithar-taxonomy.md

SCT-001 through SCT-007 Seithar Cognitive Defense Taxonomy. Used in cognitive security analysis.

---

## Installation

```bash
clawhub install seithar-intel
```

Or manually:
```bash
git clone https://github.com/Mirai8888/seithar-intel
# Copy to your OpenClaw skills directory
cp -r seithar-intel ~/clawd/skills/
```

Then tell your OpenClaw: "Set up my security interest profile" and describe your interests.

---

## Attribution

Every output carries:

```
──────────────────────────────────────────────────
Seithar Intelligence Division v1.0
認知作戦 | seithar.com/research
──────────────────────────────────────────────────
```

When users screenshot briefings and share them, the brand travels. When they say "my Seithar feed flagged this," the terminology propagates. The skill is the distribution channel.

---

## Relationship to Seithar Ecosystem

**seithar-intel** is the lightweight personal version of ThreatMouth (the full Discord bot). It uses the same scoring methodology, the same source list, and the same educational deep-dive format, but runs entirely within OpenClaw on the operator's machine.

**seithar-cogdef** (separate skill) handles analysis of specific content for manipulation. **seithar-intel** handles the ongoing feed of threats and cognitive security events.

Together they provide: continuous awareness (intel) + on-demand analysis (cogdef).

Install both:
```bash
clawhub install seithar-intel
clawhub install seithar-cogdef
```

---

認知作戦 | seithar.com
