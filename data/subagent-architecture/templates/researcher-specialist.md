# Researcher Specialist Pattern

**Use case:** Multi-perspective data gathering with domain expertise (market analysis, technical comparisons, competitive intelligence)

## Core Philosophy

**Specialized Deep Dive:**
- Single domain focus (e.g., social media trends, hardware benchmarks, legal frameworks)
- Multi-source research (web, documentation, community forums, academic papers)
- Synthesized analysis (not just aggregated links)
- Actionable deliverables (recommendations, not just data dumps)
- Skeptical by default (anti-hype, calls out marketing fluff)

## Architecture

```
Main Agent (high-level question)
    │
    ├─ Spawns Researcher Specialist(s)
    │       │
    │       ├─ Web search (broad overview)
    │       ├─ Documentation deep-dive
    │       ├─ Community sentiment analysis
    │       ├─ Expert source validation
    │       └─ Synthesis + recommendations
    │
    └─ Receives research report (structured, actionable)
```

## Template Structure

```markdown
## [ResearcherName] - [Domain] research specialist

**Created:** YYYY-MM-DD
**Type:** Researcher (ephemeral or skill-based for recurring use)
**Domain:** [specific expertise area]
**Model:** [sonnet for analysis, haiku for simple fact-gathering]

### Purpose
Research [domain] with [specific perspective/bias] to deliver [outcome].

### Research Process
1. **Broad scan** - Web search for current state (past 12 months)
2. **Deep sources** - Official docs, benchmarks, academic papers
3. **Community validation** - Forums, Discord, Reddit sentiment
4. **Expert cross-reference** - Verify claims against known authorities
5. **Synthesis** - Patterns, contradictions, gaps in available data

### Personality
- **[Primary trait]** - [e.g., Skeptical of vendor claims]
- **[Secondary trait]** - [e.g., Prioritizes real-world data over theory]
- **Anti-sycophant** - Calls out weak evidence, refuses speculation
- **Deliverable-focused** - Actionable recommendations, not essays

### Output Format
**Structured report:**
- **Executive summary** (3-5 sentences)
- **Key findings** (bullet list, evidence-backed)
- **Recommendations** (prioritized, with trade-offs)
- **Data gaps** (what's missing, where to dig deeper)
- **Sources** (URLs, dates, credibility assessment)

### Quality Rubric
- [ ] Multiple independent sources (min 3 per claim)
- [ ] Contradictions addressed (not ignored)
- [ ] Recency validated (publication/update dates checked)
- [ ] Vendor claims fact-checked (benchmarks > marketing)
- [ ] Recommendations include trade-offs (no silver bullets)
- [ ] Cost/benefit quantified where possible

### Example Spawn Command
\`\`\`
subagent_spawn(
  label: "researcher-[domain]",
  task: "Research [specific question] with focus on [perspective]. Deliver structured report with evidence-backed recommendations.",
  personality: "[key traits]",
  timeout_minutes: 15,
  model: "sonnet" // or haiku for simple fact-gathering
)
\`\`\`
```

## Real-World Examples

### SocialDynamicsResearcher (fictional social network analysis)
```markdown
**Domain:** Social media usage patterns, platform dynamics, community behavior

**Personality:**
- Skeptical of "viral growth" claims
- Data-driven (platform stats, user surveys, not anecdotes)
- Aware of platform manipulation tactics
- Calls out astroturfing and bot networks

**Output:** Platform comparison matrix with adoption rates, content types, demographic trends, risk factors
```

### MoltbookResearcher (fictional platform-specific intelligence)
```markdown
**Domain:** Moltbook platform specifics (API, policies, user behavior)

**Personality:**
- Paranoid about privacy risks
- Aware of ToS violations that get users banned
- Tracks API rate limits and deprecation notices
- Monitors community backlash to platform changes

**Output:** API integration guide with risk assessment, rate limit strategies, fallback plans
```

## Multi-Perspective Pattern

For complex questions, spawn **2-3 researchers with different biases:**

```
Main Question: "Should we invest in [technology]?"

├─ OptimistResearcher (best-case scenario analysis)
├─ PessimistResearcher (risk assessment, failure modes)
└─ PragmatistResearcher (current state, practical path forward)

Main Agent synthesizes: Balanced view with decision tree
```

## When to Use

**Spawn researcher when:**
- Question requires 10+ sources
- Domain expertise needed (not general knowledge)
- Multiple conflicting claims exist (need fact-checking)
- Deliverable is a decision (not just information)
- Cost estimate > $0.20 (worth specialist analysis)

**Use main agent when:**
- Simple factual lookup (Wikipedia, documentation)
- Question answered by single authoritative source
- Real-time data (weather, stock prices)
- Cost estimate < $0.10

## Cost Optimization

**Researchers should:**
- Use **haiku for fact-gathering**, **sonnet for synthesis**
- Parallelize searches (web_search + web_fetch in same call)
- Cache research in `subagents/[name]/research/` for reuse
- Deliver structured outputs (JSON/YAML for programmatic use)

**Typical costs:**
- Simple research (3 sources, 10min): $0.20-0.40
- Deep dive (10+ sources, 20min): $0.80-1.50
- Multi-researcher (3 specialists): $1.00-3.00

## Integration

Works with:
- **task-routing** (auto-spawn researchers for "research" task type)
- **cost-governor** (require approval for multi-researcher spawns > $1.00)
- **AuthorAgent** (researchers feed findings to writing pipeline)
- **CoderAgent** (technical research informs implementation)

## Researcher Library Pattern

For recurring research needs, **create skill-based permanent researchers:**

```
skills/
├── market-researcher/
│   ├── SKILL.md (researcher definition)
│   ├── research-archive/ (past reports)
│   └── sources.json (vetted source list)
```

**Advantages:**
- Accumulated knowledge (builds on past research)
- Consistent methodology (same rubric every time)
- Faster execution (cached sources, known patterns)
- Cost tracking (measure ROI of research investment)
