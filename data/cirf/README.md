# CIRF - Crypto Interactive Research Framework

**A structured prompt engineering framework for conducting comprehensive crypto research with AI assistance.**

**Author:** [Kudō](https://x.com/kudodefi)

---

## What is CIRF?

**CIRF (Crypto Interactive Research Framework)** is a specialized framework designed for crypto market research that emphasizes **human-AI interaction** for optimal control and output quality.

### The Problem with Autonomous AI Research

Traditional AI research approaches let models work freely and autonomously - you give a prompt, AI disappears for hours, then returns with a completed report. This creates several issues:

- ❌ No visibility into the research process
- ❌ No ability to course-correct during execution
- ❌ Outputs may miss your specific needs or priorities
- ❌ Black-box process with limited quality control

### The CIRF Approach: Interactive Collaboration

Instead of autonomous execution, CIRF transforms research into a **collaborative team session** between you and AI:

- ✅ **Continuous control** - Guide AI through each research phase
- ✅ **Real-time adjustments** - Refine focus areas as insights emerge
- ✅ **Interactive validation** - Review findings before moving forward
- ✅ **Quality assurance** - Ensure outputs match your expectations
- ✅ **Transparency** - Understand AI's reasoning at each step

Think of it as **pair programming for research** - you're the domain expert directing, AI is the research assistant executing.

**CIRF is a prompt engineering framework written entirely in natural language (YAML + Markdown) with zero lines of code.** This means you can easily read, understand, and customize any part of the framework to fit your needs.

### Flexibility: Collaborative or Autonomous

While CIRF is designed for **interactive collaboration** (recommended), it also supports **autonomous mode** when appropriate:

- **Collaborative mode** (Default) - Step-by-step guidance, review at each phase
- **Autonomous mode** (Optional) - Full workflow execution, minimal intervention

**Best practice:** Start collaborative to build understanding, then use autonomous for repetitive tasks.

---

## How It Works

CIRF enables **iterative human-AI collaboration** through continuous interaction:

```
┌─────────────────────────────────────────────┐
│         INTERACTIVE RESEARCH LOOP            │
└─────────────────────────────────────────────┘

  YOU DIRECT  →  AI RESEARCHES  →  AI CHECKS IN
      ↑                                  ↓
      │                                  ↓
      └──────  YOU REVIEW & REFINE  ←───┘
                       │
                       ↓
                 ITERATE UNTIL
                  SATISFIED
                       │
                       ↓
                 FINAL OUTPUT
```

**The Loop:**
1. **You direct** - Define goal, set priorities, provide context
2. **AI researches** - Gathers data, conducts analysis following framework methodology
3. **AI checks in** - Presents findings, asks clarifying questions
4. **You review & refine** - Validate, redirect, add expertise
5. **Iterate** - Loop continues through research phases until satisfied
6. **Final output** - AI generates structured report following template

This **continuous feedback loop** ensures research stays aligned with your goals and incorporates your expertise at every critical decision point.

---

## Requirements

### AI Assistant
This framework works with AI CLI tools that have file read/write capabilities:

- ✅ [Claude Code](https://claude.com/product/claude-code) (Recommended)
- ✅ [OpenClaw](https://openclaw.ai/)
- ✅ [Codex CLI](https://openai.com/codex/)
- ✅ Any AI assistant with file system access

### Setup
```bash
git clone https://github.com/kudodefi/cirf.git
cd cirf
```

That's it. No installation, no dependencies.

---

## Quick Start

### Method 1: Agent File Path (Recommended)

Tag the agent file directly to activate:

```
You: @framework/agents/research-analyst.yaml
     I need competitive analysis for Ethereum vs Bitcoin.
     Use collaborative mode.

AI: [Reads and embodies research analyst persona]
    Running competitive-analysis workflow in collaborative mode...
```

**Why recommended:**
- ✅ Direct and explicit
- ✅ AI knows exactly which file to read
- ✅ Works reliably across all AI tools

**Available agent files:**
- `@framework/agents/research-analyst.yaml` - Market & fundamentals
- `@framework/agents/technology-analyst.yaml` - Technical architecture
- `@framework/agents/content-creator.yaml` - Content transformation
- `@framework/agents/qa-specialist.yaml` - Quality assurance

### Method 2: Agent Tag Shorthand

Use agent name as shorthand:

```
You: @Research-Analyst - Analyze Bitcoin's market position.
     Collaborative mode.

AI: [Interprets and reads framework/agents/research-analyst.yaml]
    Starting analysis...
```

### Method 3: Natural Language

Simply describe what you want:

```
You: I want to analyze Ethereum's current market position.
     Help me understand its competitive landscape.

AI: I'll activate as Research Analyst and suggest appropriate workflows.
```

### Method 4: Orchestrator Mode

For complex multi-workflow research:

```
You: Read @SKILL.md and act as orchestrator.
     I want comprehensive analysis of Ethereum for investment decision.

AI: [Reads SKILL.md orchestration protocol]
    [Proposes multi-workflow research plan]
    [Executes with your approval at each phase]
```

---

## Framework Structure

```
cirf/
├── README.md                  # This file (for humans)
├── SKILL.md                   # Orchestration instructions (for AI)
│
├── framework/
│   ├── core-config.yaml       # Framework configuration
│   ├── _workspace.yaml        # Workspace template
│   │
│   ├── agents/                # 4 Expert personas
│   │   ├── research-analyst.yaml
│   │   ├── technology-analyst.yaml
│   │   ├── content-creator.yaml
│   │   └── qa-specialist.yaml
│   │
│   ├── workflows/             # 17 Research workflows
│   │   └── {workflow-id}/
│   │       ├── workflow.yaml
│   │       ├── objectives.md
│   │       └── template.md
│   │
│   ├── components/            # Shared execution protocols
│   └── guides/                # Research methodologies
│
└── workspaces/                # Your research projects (auto-created)
    └── {project-id}/
        ├── workspace.yaml
        ├── documents/
        └── outputs/
```

---

## Expert Agents

Each agent is a **persona definition** that AI embodies when activated.

### 🔬 Research Analyst
**Expertise:** Market intelligence, project fundamentals, investment synthesis
**Use for:** Market analysis, project evaluation, competitive research, investment thesis
**Workflows:** All research workflows

**Activate:**
```
@framework/agents/research-analyst.yaml
```

### ⚙️ Technology Analyst
**Expertise:** Architecture assessment, security analysis, technical evaluation
**Use for:** Smart contract review, protocol architecture, technical due diligence
**Workflows:** technology-analysis

**Activate:**
```
@framework/agents/technology-analyst.yaml
```

### ✍️ Content Creator
**Expertise:** Research-to-content transformation, multi-platform optimization
**Use for:** Converting research into X threads, blog articles, YouTube scripts
**Workflows:** create-content

**Activate:**
```
@framework/agents/content-creator.yaml
```

### ✓ QA Specialist
**Expertise:** Quality validation, critical review, bias detection
**Use for:** Reviewing research outputs, challenging assumptions, finding gaps
**Workflows:** qa-review

**Activate:**
```
@framework/agents/qa-specialist.yaml
```

---

## Workflows

Each workflow is a **structured research process** with defined methodology and output template.

### Setup & Planning
| Workflow ID | Description |
|-------------|-------------|
| `framework-init` | First-time user configuration |
| `create-research-brief` | Define research scope & objectives |

### Market Intelligence
| Workflow ID | Description |
|-------------|-------------|
| `sector-overview` | Sector structure, dynamics, key players |
| `sector-landscape` | Ecosystem mapping, player categorization |
| `competitive-analysis` | Head-to-head project comparison |
| `trend-analysis` | Trend identification & forecasting |

### Project Fundamentals
| Workflow ID | Description |
|-------------|-------------|
| `project-snapshot` | Quick project overview |
| `product-analysis` | Product mechanics, PMF, innovation |
| `team-and-investor-analysis` | Team background, investor quality |
| `tokenomics-analysis` | Token economics, sustainability |
| `traction-metrics` | Growth, retention, unit economics |
| `social-sentiment` | Community health, sentiment |

### Technical & Quality
| Workflow ID | Description |
|-------------|-------------|
| `technology-analysis` | Architecture, security, code quality |
| `qa-review` | Validation, bias detection, gap analysis |

### Content & Flexible
| Workflow ID | Description |
|-------------|-------------|
| `create-content` | Multi-format content package |
| `open-research` | Custom research on any topic |
| `brainstorm` | Ideation and exploration |

---

## Workspace & Output Management

Each research project gets its own workspace for organization and isolation.

### Workspace Structure
```
workspaces/{project-id}/
├── workspace.yaml          # Project metadata & configuration
├── documents/              # Source materials, references
└── outputs/                # Generated research deliverables
    └── {workflow-id}/
        └── {workflow-id}-{date}.md
```

### How It Works

**AI automatically manages workspaces:**

```
You: Analyze Ethereum for investment.

AI: Creating workspace 'ethereum'...
    ✅ Workspace ready: workspaces/ethereum/
    Starting research...
```

**Outputs are auto-saved with version control:**

```
outputs/sector-overview/
├── sector-overview-2025-02-09.md  # Latest
├── sector-overview-2025-02-01.md  # Previous
└── sector-overview-2025-01-15.md  # Initial
```

**Context preserved across sessions:**

```
Session 1: sector-overview
Session 2: competitive-analysis (builds on session 1 context)
Session 3: synthesis (consolidates all previous work)
```

---

## Best Practices

### 1. Prefer Collaborative Mode

**Why collaborative is recommended:**
- ✅ Quality control at each phase
- ✅ Inject domain expertise when needed
- ✅ Course-correct as insights emerge
- ✅ Ensure outputs match expectations

**When to use autonomous:**
- ✅ Repetitive analysis with clear requirements
- ✅ After calibrating AI's approach collaboratively
- ✅ Time-sensitive updates using established framework

### 2. Build Research in Phases

Don't try to do everything at once:

```
Phase 1: sector-overview (market context)
Phase 2: project-snapshot (subject overview)
Phase 3: Specialized deep-dives (based on Phase 1-2 findings)
Phase 4: Synthesis (investment thesis or recommendation)
```

### 3. Use Research Briefs for Complex Projects

Define clear objectives upfront:

```
You: Create research brief for Ethereum analysis.

AI: [Helps structure objectives, scope, approach]
    [Suggests workflow sequence]
```

### 4. Leverage AI for Research, You for Judgment

**AI excels at:** Data gathering, synthesis, pattern identification
**You excel at:** Strategic direction, domain expertise, investment judgment

```
You: Analyze competitive moat. I believe network effects matter more than tech specs.

AI: Understood. Weighting analysis: High priority on network effects, switching costs.
    [Executes with your strategic framing]
```

### 5. Iterate on Outputs

Don't settle for first draft:

```
AI: Report complete.

You: Competitive landscape needs more depth. Add emerging players.

AI: [Refines section]
    Better?

You: Good. Now add risk factors for each incumbent.

AI: [Final version saved]
```

### 6. Use QA Review for Critical Decisions

Validate important research:

```
You: @framework/agents/qa-specialist.yaml
     Review my Ethereum investment analysis.

AI: ⚠️ Potential bias: Heavy weight on developer ecosystem, value accrual link unclear.
    📊 Gap: Missing regulatory risk for DeFi platforms.
    ❓ Logic: Bull case assumes L2 success but doesn't model fragmentation risk.

    Recommend addressing before final decision.
```

### 7. Start Broad, Then Go Deep

**Recommended sequence:**
1. Sector-overview (context)
2. Project-snapshot (overview)
3. Specialized workflows (deep dives)
4. Synthesis (conclusions)

### 8. Use Autonomous for Monitoring

After initial collaborative research, use autonomous for updates:

```
Initial: Comprehensive Bitcoin analysis (collaborative, multi-session)
3 months later: Update with Q1 2025 data (autonomous, same framework)
```

---

## Troubleshooting

### AI doesn't understand framework
**Solution:** Explicitly tell AI to read framework files
```
You: Read @SKILL.md first, then help me with research.
```

### Outputs not following template
**Solution:** Remind AI to follow template
```
You: Execute sector-overview. Follow template.md exactly.
```

### Research lacks depth
**Solution:** Specify research depth
```
You: Run product-analysis with deep research depth.
     Follow methodology in framework/guides/research-methodology.md.
```

---

## Contributing

Found issues or have suggestions?
[Open an issue](https://github.com/kudodefi/cirf/issues) or submit a pull request.

---

## License

MIT License - See LICENSE file for details.

---

## Credits

**Created by:** [Kudō](https://x.com/kudodefi)
**Framework Version:** 1.0.0
**Last Updated:** 2025-02-09

---

**Ready to start researching?**

```
You: @research-analyst.yaml
     Help me research [your topic]
```
