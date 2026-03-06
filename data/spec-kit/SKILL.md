---
name: spec-kit
description: Use GitHub Spec Kit for Spec-Driven Development. Initialize projects, create specifications, and build software using the /speckit.* slash commands. Supports Claude Code, GitHub Copilot, Gemini CLI, and Codebuddy.
metadata:
  {
    "openclaw":
      {
        "emoji": "📋",
        "requires": { "bins": ["uv", "python3", "git"] },
      },
  }
---

# Spec Kit — Spec-Driven Development

Build high-quality software faster using **Spec-Driven Development** (SDD). Specifications become executable artifacts that generate working implementations, not just documentation.

**Homepage:** https://github.github.com/spec-kit/  
**GitHub:** https://github.com/github/spec-kit

---

## What is Spec-Driven Development?

SDD flips traditional software development:

| Traditional | Spec-Driven |
|-------------|-------------|
| Specs are scaffolding → discarded | Specs are **executable** → generate code |
| Code is king | **Intent** is king |
| One-shot prompts | Multi-step refinement |
| Focus on "how" | Focus on "what" and "why" |

**Core Philosophy:**
- Intent-driven development
- Rich specifications with guardrails
- Heavy reliance on AI model capabilities
- Technology-independent process

---

## Prerequisites

- **OS:** Linux, macOS, Windows (PowerShell supported)
- **AI Agent:** Claude Code, GitHub Copilot, Gemini CLI, or Codebuddy CLI
- **Package Manager:** [uv](https://docs.astral.sh/uv/)
- **Python:** 3.11+
- **Git:** Any recent version

---

## Installation & Setup

### Initialize a New Project

```bash
# Create new project directory
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>

# Initialize in current directory
uvx --from git+https://github.com/github/spec-kit.git specify init .
uvx --from git+https://github.com/github/spec-kit.git specify init --here
```

### Specify AI Agent

```bash
# Proactively set AI agent during init
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --ai claude
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --ai gemini
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --ai copilot
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --ai codebuddy
```

### Script Type (Shell vs PowerShell)

Auto-selected by OS, or force explicitly:

```bash
# Force PowerShell (Windows)
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --script ps

# Force POSIX shell (Linux/macOS)
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --script sh
```

### Skip Tool Checks

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init <project> --ai claude --ignore-agent-tools
```

---

## The 6-Step Spec-Driven Process

### Step 1: Initialize

Run `specify init` to create project structure with templates.

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init my-app --ai claude
```

**Creates:**
- `.speckit/` directory with configuration
- Agent-specific templates
- Git repository structure

---

### Step 2: Define Constitution

Establish core rules and principles for your project.

**Slash Command:**
```
/speckit.constitution This project follows a "Library-First" approach. 
All features must be implemented as standalone libraries first. 
We use TDD strictly. We prefer functional programming patterns.
```

**Purpose:** Sets guardrails and organizational principles that all specs must follow.

---

### Step 3: Create Specification

Describe **what** you want to build, not **how**.

**Slash Command:**
```
/speckit.specify Build an application that can help me organize my photos 
in separate photo albums. Albums are grouped by date and can be re-organized 
by dragging and dropping on the main page. Albums are never in other nested 
albums. Within each album, photos are previewed in a tile-like interface.
```

**Best Practices:**
- Focus on user scenarios and behaviors
- Avoid tech stack details (AI picks appropriate tech)
- Describe UI/UX in plain language
- Include constraints and business rules

---

### Step 4: Refine (Clarify)

Identify and resolve ambiguities in your specification.

**Slash Command:**
```
/speckit.clarify Focus on security implications and edge cases
```

**What it does:**
- Detects vague or ambiguous requirements
- Asks clarifying questions
- Suggests concrete implementations
- Updates spec with resolved details

---

### Step 5: Plan

Generate detailed implementation plan from specification.

**Slash Command:**
```
/speckit.plan
```

**Output:**
- Architecture decisions
- File structure
- Implementation steps
- Testing strategy
- Dependencies to install

---

### Step 6: Build

Execute the implementation plan.

**Slash Command:**
```
/speckit.build
```

**Features:**
- Generates code based on spec + plan
- Creates files incrementally
- Runs tests as specified
- Commits progress to Git

---

## Context Awareness: Git Branch-Based

Spec Kit automatically detects the active feature based on your current Git branch.

**Naming Convention:**
```
001-feature-name
002-user-authentication
003-photo-album-grid
```

**To switch between specifications:**
```bash
git checkout 001-feature-name    # Work on feature 1
git checkout 002-user-auth       # Work on feature 2
```

**Context is automatically loaded** when you run Spec Kit commands.

---

## Development Phases

### Phase 1: 0-to-1 (Greenfield)
**Focus:** Generate from scratch

- Start with high-level requirements
- Generate specifications
- Plan implementation steps
- Build production-ready applications

### Phase 2: Creative Exploration
**Focus:** Parallel implementations

- Explore diverse solutions
- Support multiple technology stacks
- Experiment with UX patterns
- Compare approaches

### Phase 3: Iterative Enhancement (Brownfield)
**Focus:** Modernization

- Add features iteratively
- Modernize legacy systems
- Adapt existing processes
- Refactor with specs

---

## All Slash Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/speckit.constitution` | Define project principles | At project start |
| `/speckit.specify` | Create specification | For each new feature |
| `/speckit.clarify` | Resolve ambiguities | When spec is vague |
| `/speckit.plan` | Generate implementation plan | Before coding |
| `/speckit.build` | Execute implementation | After planning |

---

## Enterprise Features

### Organizational Constraints

- **Cloud Providers:** Target specific platforms (AWS, Azure, GCP)
- **Tech Stacks:** Enforce approved technologies
- **Design Systems:** Integrate enterprise UI libraries
- **Compliance:** Meet security/regulatory requirements

### Technology Independence

Spec Kit works with:
- Any programming language
- Any framework
- Any architecture pattern
- Any deployment target

---

## Local Development (Contributing)

### Clone and Setup

```bash
git clone https://github.com/github/spec-kit.git
cd spec-kit
```

### Run CLI Directly

```bash
# Fastest feedback - no install needed
python -m src.specify_cli --help
python -m src.specify_cli init demo-project --ai claude --script sh
```

### Editable Install

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
uv pip install -e .
specify --help
```

### Test From Branch

```bash
# Push branch first
git push origin your-feature-branch

# Test via uvx
uvx --from git+https://github.com/github/spec-kit.git@your-feature-branch \
  specify init demo-branch-test --script ps
```

---

## Best Practices

### Specification Writing

✅ **DO:**
- Describe user scenarios
- Include business rules
- Mention constraints
- Use plain language
- Focus on behavior, not implementation

❌ **DON'T:**
- Specify tech stack (let AI choose)
- Write implementation details
- Use jargon without context
- Make assumptions unstated

### Example Good Spec

```
/speckit.specify Build a task management app where:
- Users can create projects with color-coded labels
- Tasks have priorities (High/Medium/Low) with visual indicators
- Drag-and-drop to reorder tasks within a project
- Tasks can be assigned to multiple users
- Due dates trigger notifications 24h before
- Completed tasks archive automatically after 7 days
- Mobile-responsive with touch-friendly interactions
```

### Example Bad Spec

```
/speckit.specify Build a React app with Redux for state management.
Use Material-UI for components. Store data in PostgreSQL.
```

---

## Troubleshooting

### Command Not Found

**Problem:** AI agent doesn't recognize `/speckit.*` commands  
**Solution:** Re-run `specify init` in the project directory

### Wrong Context Loaded

**Problem:** Working on wrong specification  
**Solution:** Check current branch with `git branch` and switch: `git checkout <branch>`

### Script Type Issues

**Problem:** PowerShell scripts on macOS or vice versa  
**Solution:** Force script type: `--script sh` or `--script ps`

### Agent Tool Missing

**Problem:** Spec Kit complains about missing AI agent tools  
**Solution:** Use `--ignore-agent-tools` flag during init

---

## Workflow Examples

### New Feature Workflow

```bash
# 1. Create feature branch
git checkout -b 004-dark-mode

# 2. In AI agent chat:
/speckit.specify Add dark mode toggle to the application. 
System should detect OS preference but allow manual override. 
Store preference in localStorage.

# 3. Clarify ambiguities:
/speckit.clarify Focus on accessibility (WCAG contrast)

# 4. Generate plan:
/speckit.plan

# 5. Build:
/speckit.build

# 6. Commit and PR
git add .
git commit -m "feat: add dark mode toggle"
```

### Brownfield Enhancement

```bash
# 1. Switch to existing feature
git checkout 002-user-auth

# 2. Enhance spec:
/speckit.specify Add OAuth2 login with Google and GitHub providers

# 3. Plan the enhancement:
/speckit.plan

# 4. Build iteratively:
/speckit.build
```

---

## Resources

- **Documentation:** https://github.github.com/spec-kit/
- **GitHub Repo:** https://github.com/github/spec-kit
- **Contributing:** https://github.com/github/spec-kit/blob/main/CONTRIBUTING.md
- **Support:** https://github.com/github/spec-kit/blob/main/SUPPORT.md

---

## Key Principles Summary

1. **Intent over Implementation** — Describe what, not how
2. **Specifications are Assets** — Treat them as primary deliverables
3. **Multi-step Refinement** — Iterate: Constitute → Specify → Clarify → Plan → Build
4. **Context-Aware** — Git branches maintain feature context
5. **Technology Agnostic** — Process works with any stack

---

_Last updated: 2026-02-28_
