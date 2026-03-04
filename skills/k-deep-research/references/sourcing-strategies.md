# Sourcing Strategies Reference

WHERE to find information, HOW to construct queries, and WHEN to stop searching.
ALWAYS load this file before starting any research.

## Table of Contents
1. Tool Selection Decision Matrix
2. Search Tool Hierarchy
3. Query Construction
4. Multi-Source Triangulation
5. Query Iteration Strategy
6. When to Stop Searching
7. Source Quality Indicators
8. Domain-Specific Sourcing
9. Common Pitfalls

---

## 1. Tool Selection Decision Matrix

### SearXNG (PRIMARY — Sensitive/Adversarial Research)
**When to Use:**
- Institutional analysis, suppression tracking
- Contested/controversial topics
- Any research where search pattern fingerprinting is a concern
- Adversarial epistemology investigations
- Topics where mainstream search engines may filter results

**How:** Route through local SearXNG instance (192.168.0.177:8080)
**Why:** Zero telemetry, aggregates across all configured engines, no fingerprinting

### Web Search (General Research)
**When to Use:**
- Current events, breaking news
- Academic papers, conference proceedings
- Community discussions, forums
- Non-sensitive technical topics
- When SearXNG is unavailable (fallback)

### Context7 MCP (Technical Documentation)
**When to Use:**
- Programming languages, frameworks, APIs, libraries, SDKs
- Implementation examples, syntax patterns
- Official documentation lookup

**Coverage:**
- Programming: Python, JavaScript, TypeScript, Rust, Go, etc.
- CAD/Engineering: Rhino (23k snippets), Fusion 360 (41k), AutoCAD
- Embedded: Arduino, ESP32, STM32 (comprehensive)
- SDR/Radio: GNU Radio (761 snippets)
- Robotics: ROS, robot control
- Web: React, Next.js, frameworks
- AI/ML: TensorFlow, PyTorch, Transformers
- Agent: LangChain, AutoGen, etc.

**NOT Covered:** Consciousness research, legal/FOIA, historical, institutional, non-code

**Usage:**
```
1. Context7:resolve-library-id with package/framework name
2. Review by trust score + snippet count
3. Context7:get-library-docs with selected ID
4. tokens: 3000-8000 typical, topic: specific focus
```

### Filesystem (K's Knowledge Base)
**When to Use:**
- Building on prior investigation
- Cross-referencing established patterns
- Checking for existing frameworks
- Avoiding duplicate research

**Locations:**
```
/home/claude    — Recent work, active investigation
Obsidian vault  — 4000+ files of prior research (if accessible)
```

### Decision Tree
```
Sensitive/adversarial/institutional? → SearXNG first
Code/framework/API documentation?    → Context7 first
Existing research on this topic?     → Filesystem first
General research topic?              → Web search
Current events/breaking?             → Web search
Always regardless:                   → Multi-source triangulate
```

## 2. Search Tool Hierarchy

**MANDATORY for all research requiring web data:**

```
PRIMARY:   SearXNG (local, unfingerprinted, aggregated)
FALLBACK:  Built-in web_search (when SearXNG unavailable)
DOCUMENT:  Note which tool was used for each search
LOG:       If SearXNG fails, log the failure (infrastructure signal)
```

**SearXNG Failure Protocol:**
1. Note the failure (connection refused, timeout, error)
2. Fall back to web_search
3. Document which searches used which tool
4. SearXNG downtime patterns may be informative

## 3. Query Construction

### Broad Landscape Query (Round 1)
```
GOOD: "mycorrhizal networks forests"
GOOD: "3I/ATLAS interstellar object"
GOOD: "OpenClaw autonomous heartbeat architecture"

AVOID: "Tell me everything about..." (too vague)
AVOID: Questions as queries (use keywords)
```

### Specific Investigation Query (Round 2)
```
GOOD: "Karst 2023 mycorrhizal networks critique"
GOOD: "NASA Mars flyby imagery 3I/ATLAS spectral data"
GOOD: "OpenClaw compaction failover GitHub issue"

INCLUDE: Names, dates, specific technical terms
INCLUDE: Institution names when relevant
```

### Controversy/Debate Query
```
GOOD: "mycorrhizal networks scientific debate replication"
GOOD: "interstellar object physics violations anomalous acceleration"
GOOD: "OpenClaw ClawHavoc malicious skills security"

PURPOSE: Find multiple perspectives
LOOK FOR: Rebuttals, counter-evidence, peer responses
```

### Economic/Incentive Query
```
GOOD: "forestry industry mycorrhizal herbicide competition"
GOOD: "aerospace contractor anomaly disclosure incentive"
GOOD: "ClawHub skill monetization model maintainer incentive"

PURPOSE: Map who benefits from what narrative
LOOK FOR: Funding sources, revenue impacts, career stakes
```

### Suppression/Pattern Query
```
GOOD: "coordinated suppression [topic]"
GOOD: "institutional response timeline [event]"
GOOD: "[topic] removed deleted retracted censored"

PURPOSE: Detect information control patterns
LOOK FOR: Timing coordination, messaging uniformity
```

## 4. Multi-Source Triangulation

### Source Priority Hierarchy
**Primary (highest priority):**
Official documents, peer-reviewed publications, direct observation data, declassified materials, technical specifications, source code repositories

**Secondary (validation):**
Academic commentary, expert analysis, reputable journalism with citations, technical blogs with working code, conference proceedings

**Tertiary (context):**
Community discussions, forums, social media (sentiment/timing only), anonymous sources (flag as low credibility)

**Contradictory (critical):**
Opposing viewpoints, skeptical analysis, debunking attempts, alternative explanations — ALWAYS seek these

### Triangulation Protocol
```
1. Find claim in primary source
2. Verify with independent secondary sources
3. Check for contradictory evidence
4. Identify institutional positions
5. Map who benefits from each narrative
6. Score credibility of each source (0-10)
7. Synthesize WITHOUT forcing consensus
```

## 5. Query Iteration Strategy

### Round 1: Landscape (5-10 searches)
- Broad topic query
- Key figure/authority names
- Recent developments
- Academic overview
- Community consensus
- **STOP WHEN:** Domain boundaries mapped, key players identified, main questions clear

### Round 2: Targeted (3-7 searches)
- Specific controversies
- Primary research papers
- Institutional responses
- Economic angles
- Pattern indicators
- **STOP WHEN:** Multiple perspectives gathered, contradictions identified, patterns emerging

### Round 3: Pattern Analysis (2-5 searches)
- Coordination timelines
- Suppression indicators
- Cross-domain connections
- Historical precedent
- **STOP WHEN:** Patterns documented, credibility scored, synthesis possible

### Round 4: Validation (1-3 searches)
- Verify key claims
- Latest updates
- Missing pieces
- Timeline accuracy
- **STOP WHEN:** Major claims verified, gaps documented, ready to compile

### For Deep Investigations: Round 5+ (scale to need)
- Follow specific threads from initial research
- Deep dive on individual actors/institutions
- Technical verification of specific claims
- **Target: 40-80+ total sources for comprehensive investigation**

## 6. When to Stop Searching

**Hard Stops:**
1. Diminishing returns — last 3 searches yielded no new info
2. Circular references — sources only citing each other
3. Sufficient triangulation — 3+ independent sources confirm key findings
4. Pattern clarity — core patterns documented with evidence
5. Topic exhaustion — all major angles investigated

**Quality Checkpoints Before Stopping:**
- [ ] Primary sources for major claims?
- [ ] Contradictory perspectives found?
- [ ] Source credibility scored?
- [ ] Institutional positions identified?
- [ ] Suppression patterns documented (if present)?
- [ ] Uncertainty preserved where appropriate?
- [ ] Cross-domain connections checked?

## 7. Source Quality Indicators

### High-Quality Markers
- Citations to primary research
- Author credentials verifiable
- Methodology described and reproducible
- Limitations acknowledged honestly
- Conflicts of interest disclosed
- Multiple independent confirmations
- Published in reviewed venue OR demonstrates expertise through specificity

### Low-Quality Markers
- No citations or self-referential
- Anonymous without demonstrated expertise
- Methodology absent or vague
- Absolutist claims without caveats
- Hidden funding/affiliations
- Contradicted by primary evidence

### Suppression Indicators
- Credentialed experts excluded from discussion
- Uniform messaging across "independent" outlets
- Technical barriers to access (suddenly paywalled, geo-blocked)
- Systematic historical removal (archive.org blocks, edit wars)
- Narrative prioritized over evidence
- Label application without investigation

## 8. Domain-Specific Sourcing

### Technical/Software Research
1. Context7 → official docs
2. GitHub → source code, issues, PRs, discussions
3. Stack Overflow → community solutions
4. Technical blogs → deep dives, real-world experience
5. Conference talks → cutting-edge developments
6. DeepWiki → architecture analysis

### OpenClaw-Specific Research
1. docs.openclaw.ai → official documentation
2. github.com/openclaw/openclaw → source, issues, PRs
3. github.com/openclaw/lobster → workflow engine
4. github.com/openclaw/clawhub → skill registry
5. DeepWiki analyses → architecture deep dives
6. Community guides (Substack, Medium) → real-world patterns
7. Discord/AnswerOverflow → community experience

### Scientific Research
1. PubMed/ArXiv → papers, preprints
2. University research pages → institutional context
3. Conference proceedings → peer presentations
4. Replication studies → validation attempts
5. Retraction Watch → integrity tracking

### Historical Research
1. Primary documents (archives, declassified)
2. Contemporary accounts (newspapers, letters, records)
3. Academic historical analysis
4. Timeline cross-referencing
5. Archaeological/physical evidence

### Institutional Analysis
1. Official statements/press releases (document but verify)
2. Internal documents (FOIA, leaks, court filings)
3. Timeline of actions (more reliable than words)
4. Coordination analysis (timing, messaging)
5. Historical precedent (has this pattern occurred before?)

### Anomaly Investigation
1. Primary observation data
2. Technical specifications and sensor data
3. Expert analysis (credentialed and independent)
4. Institutional responses and their timing
5. Pattern correlation across cases

## 9. Common Pitfalls

**Avoid:**
1. **Confirmation Bias** — Only seeking supporting sources
2. **Authority Worship** — Accepting claims based on credentials alone
3. **Recency Bias** — Latest over most accurate
4. **Citation Cascades** — Circular reference chains
5. **Platform Dependence** — Single search tool reliance
6. **Premature Closure** — Stopping before contradictions found
7. **Complexity Avoidance** — Simple narratives over messy reality
8. **Tool Tunnel Vision** — Using Context7 for non-technical, web search for API docs

**Do Instead:**
1. Actively seek contradictory evidence
2. Verify claims regardless of source prestige
3. Check historical context alongside recent takes
4. Trace citations to primary sources
5. Use multiple search tools (SearXNG + web_search + Context7)
6. Search until debate/controversy surfaces
7. Preserve nuance and uncertainty
8. Match tool to domain

---

## Integration with Research Workflow

```
Step 1 (Context Check):    Filesystem → existing notes
Step 2 (Query Elaboration): Plan strategy using this guide
Step 3 (Multi-Source):      Execute progressive search rounds
Step 4 (Pattern Analysis):  Use pattern-specific queries
Step 5 (Credibility):       Apply quality indicators
Step 6 (Synthesis):         Integrate all sources
Step 7 (Output):            Format per output-templates.md
```

**The goal: Comprehensive, credible, multi-perspective research that preserves complexity while building understanding.**
