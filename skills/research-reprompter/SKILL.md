---
name: research-reprompter
description: |
  Transform rough research questions into executable USACF research prompts.
  Use when user says "research", "research this", "investigate", "deep dive",
  "researcher", or pastes a research topic. Generates complete multi-agent swarm
  configuration with algorithm selection, claude-flow commands, and adversarial review.
compatibility: |
  Full features require Claude Code with claude-flow installed (npx claude-flow@alpha).
  Core prompt generation works on all Claude surfaces.
metadata:
  version: 2.0.0
---

# Researcher v2.0 (USACF Research Generator)

> **Voice-to-research engineering for Claude Code. Transform rough questions into executable USACF swarm configurations.**

## Changelog

| Version | Changes |
|---------|---------|
| **v2.0** | Full USACF integration: algorithm selection, claude-flow commands, adversarial review, fact-checking, memory namespaces |
| v1.0 | Initial version based on Reprompter v4.1 |

## Purpose

Turn your rough research questions into complete, executable multi-agent research prompts using the USACF framework.

**The Problem:**
- Research questions are often vague and unstructured
- Manual setup of research swarms is tedious
- Missing adversarial review leads to blind spots
- No systematic algorithm selection

**The Solution:**
Smart interview → USACF super-prompt with all phases, agents, and commands.

---

## Process (4 steps)

### Step 1: Receive raw input
Accept the user's rough research question (dictated, typed messily, or incomplete).

**Trigger words:** `research`, `investigate`, `deep dive`, `analyze`, `research this`

### Step 2: Complexity detection
**Auto-detect complexity to select algorithm:**
- Simple (< 20 words, single topic) → CoT, 1-3 agents
- Medium (branching, comparison) → ToT, 4-8 agents
- Complex (comprehensive, multi-domain) → GoT, 9-15 agents

### Step 3: Smart interview (gather user input)
Gather:
1. **Research Title** - Name for this research
2. **Subject** - What we're researching
3. **Subject Type** - Product / Software / Business / Process / Organization
4. **Research Type** - Competitive / Gap / Technical / Due Diligence / Market
5. **Objectives** - What to find out (1-20, one per line)
6. **Constraints** - Focus areas, limitations (optional)
7. **Depth** - CoT / ToT / GoT
8. **Output** - Brief / Full Report / Action Plan / Raw

### Step 4: Generate USACF super-prompt + score
Generate complete executable configuration with:
- Initialization commands
- All phase agents (Discovery, Analysis, Adversarial, Synthesis)
- Memory operations
- Final report generator
- Quality score comparison

---

## CRITICAL: MUST GENERATE COMPLETE SUPER-PROMPT

**After interview completes, you MUST immediately:**

1. **Select algorithm** (CoT/ToT/GoT) based on complexity
2. **Generate full USACF super-prompt** with ALL phases
3. **Include claude-flow commands** for every operation
4. **Add adversarial review agents** (red-team, fact-checker)
5. **Show quality score** (before/after comparison)
6. **Offer to execute or copy**

```text
WRONG: Generate simple prompt without agents
RIGHT: Generate full USACF config with all phases, agents, memory ops
```

---

## Algorithm selection matrix

| Complexity | Algorithm | Topology | Agents | When to Use |
|------------|-----------|----------|--------|-------------|
| Simple | Chain-of-Thought (CoT) | Star | 1-3 | "What is X?" Single topic |
| Medium | Tree-of-Thought (ToT) | Hierarchical | 4-8 | "Compare X vs Y" Branching |
| Complex | Graph-of-Thought (GoT) | Mesh/Hive | 9-15+ | "Comprehensive analysis" |

**Complexity Indicators:**
- Simple: Single topic, factual question, < 20 words
- Medium: "compare", "vs", "evaluate", "options"
- Complex: "comprehensive", "gaps and opportunities", multiple domains

---

## USACF phases (all required for complex research)

### Phase 0: Initialization
```bash
npx claude-flow@alpha init --force
npx claude-flow@alpha swarm init --topology {topology} --max-agents {N}
npx claude-flow@alpha memory store "session/config" '{...}' --namespace search
```

### Phase 0.5: Meta-analysis
- Step-back prompting (principles, criteria)
- Self-ask decomposition (15-20 questions)
- Research planning (ReWOO)

### Phase 1: Discovery (Parallel)
- component-identifier
- hierarchy-analyzer
- interface-mapper
- flow-tracer

### Phase 2: Analysis (Parallel)
- 6 gap hunters (quality, performance, security, structural, capability, UX)
- 4 risk analysts (FMEA, edge cases, vulnerabilities, reliability)

### Phase 2.5: Adversarial review (critical)
- **red-team-reviewer**: Challenge ALL findings
- **fact-checker**: RAG verification with web_search
- **coordinator**: Integrate feedback, update confidence

### Phase 3: Synthesis (Parallel)
- quick-win-generator (0-3 months)
- strategic-generator (3-12 months)
- transformational-generator (12-36 months)
- pareto-optimizer (multi-objective portfolios)

### Phase 4: Final report
- Ultra-brief (3 sentences)
- Executive summary
- Top 10 findings with confidence
- Recommended actions by horizon
- Limitations & uncertainties

---

## Memory namespace convention

All agents store to namespaced memory:

```bash
# Session
session/config          # Research configuration

# Meta
meta/principles         # Core principles
meta/questions          # Decomposed questions
meta/research-plan      # Planned tasks

# Discovery
discovery/components    # Identified components
discovery/hierarchy     # Structural map
discovery/interfaces    # APIs/contracts
discovery/flows         # Data/control flows

# Gaps
gaps/quality            # Quality gaps
gaps/performance        # Performance gaps
gaps/security           # Security gaps

# Risks
risks/fmea              # Failure mode analysis
risks/edge-cases        # Edge cases
risks/vulnerabilities   # Security vulnerabilities

# Adversarial
adversarial/critiques   # Red team challenges
adversarial/fact-check  # Verified claims

# Opportunities
opportunities/quick-wins        # 0-3 month wins
opportunities/strategic         # 3-12 month plays
opportunities/transformational  # 12-36 month bets
opportunities/pareto-recommendation  # Optimal portfolio

# Output
output/final-report     # Comprehensive report
```

---

## Quality scoring

**Always show before/after metrics:**

| Dimension | Before | After | Change |
|-----------|--------|-------|--------|
| Clarity | X/10 | X/10 | +X% |
| Algorithm Selection | 0/10 | 10/10 | +∞ |
| Agent Design | 0/10 | 9/10 | +∞ |
| Memory Ops | 0/10 | 10/10 | +∞ |
| Adversarial | 0/10 | 9/10 | +∞ |
| Fact Checking | 0/10 | 8/10 | +∞ |
| **Overall** | **X/10** | **9+/10** | **+2000%+** |

---

## Example

**Before (rough input):**
> "look into what solana is doing with AI and how we compare"

**After (USACF super-prompt):**

```markdown
# USACF Research: Solana AI Competitive Analysis

## Configuration
- Algorithm: ToT (medium complexity - comparison)
- Topology: Hierarchical
- Agents: 8
- Output: Executive Brief

## Phase 0: Initialization
[claude-flow init commands]

## Phase 1: Discovery
[4 parallel agents with memory stores]

## Phase 2: Analysis
[Gap hunters + risk analysts]

## Phase 2.5: Adversarial
[Red team + fact checker]

## Phase 3: Synthesis
[Opportunity generators + pareto optimizer]

## Phase 4: Report
[Final report generator]

Quality: 1.2/10 → 9.3/10 (+675%)
```

---

## Tips for best results

- **Be specific about competitors** - Name them in the input
- **Mention constraints early** - "focus on Q1", "executive-level"
- **State objectives** - Even rough ones help
- **Say "expand"** - For full interview on simple queries
- **Say "quick"** - To skip interview for simple research

---

## Comparison: Reprompter vs Researcher

| Aspect | Reprompter | Researcher |
|--------|------------|------------|
| **Trigger** | "reprompt" | "research" / "researcher" |
| **Purpose** | General prompts | Research prompts |
| **Output** | Structured prompt | USACF swarm config |
| **Agents** | None | 8-15 parallel agents |
| **Memory** | No | Full namespace system |
| **Adversarial** | No | Red team + fact checker |
| **Algorithm** | No | CoT/ToT/GoT selection |
