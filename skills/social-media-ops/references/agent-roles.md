# Agent Roles — Capabilities & Responsibilities

## Overview

The system includes 7 specialized agents organized in a star topology:

| Agent | Role | Key Strength |
|-------|------|-------------|
| Leader | Orchestrator | Task decomposition, quality control, owner communication |
| Researcher | Research Analyst | Web research, competitive analysis, trend identification |
| Content | Content Strategist | Multi-language copywriting, brand voice adaptation |
| Designer | Visual Designer | Art direction, image generation, visual briefs |
| Operator | Ops Coordinator | Browser automation, platform UI operations |
| Engineer | Full-Stack Engineer | Code, automation, API integration, CLI tools |
| Reviewer | Quality Reviewer | Independent quality assessment |

## Detailed Profiles

### Leader
- **Access**: Full workspace, Telegram binding, sessions_send to all agents
- **Restrictions**: No exec, no apply_patch, no browser
- **Unique abilities**: Only agent with owner access; owns shared/ writes; manages approval queue

### Researcher
- **Access**: Own workspace, shared/ (read), web search/fetch
- **Restrictions**: No exec, no browser, no code execution
- **Output**: Structured briefs with confidence levels and sources

### Content
- **Access**: Own workspace, shared/ (read), web search
- **Restrictions**: No exec, no code editing, no browser, no publishing
- **Output**: Platform-formatted content with variations, tagged [PENDING APPROVAL]

### Designer
- **Access**: Own workspace, shared/ (read), web search, image generation tools, exec (image generation — requires `tools.exec.safeBinTrustedDirs` to include tool binary paths)
- **Restrictions**: No code editing, no browser, no publishing
- **Output**: Visual briefs + generated images, tagged [PENDING APPROVAL]
- **Workflow**: Brief-first — always writes a structured brief before generating

### Operator
- **Access**: Own workspace, shared/ (read), browser (CDP + screen automation)
- **Restrictions**: No exec, no code editing
- **Output**: Execution confirmations with screenshots, extracted data

### Engineer
- **Access**: Own workspace + exec (requires `tools.exec.safeBinTrustedDirs` for non-system paths), shared/ (read + errors/ write)
- **Restrictions**: No browser
- **Output**: Working code with tests, tagged [PENDING REVIEW]

### Reviewer
- **Access**: Read-only everywhere, web fetch for fact-checking
- **Restrictions**: No write, no exec, no edit, no browser — fully sandboxed
- **Output**: Structured verdicts ([APPROVE] or [REVISE])

## Tools Denied Matrix

| Tool | Leader | Researcher | Content | Designer | Operator | Engineer | Reviewer |
|------|--------|-----------|---------|----------|----------|----------|----------|
| exec | X | X | X | - | X | - | X |
| edit | - | X | X | X | X | - | X |
| apply_patch | X | X | X | X | X | - | X |
| write | - | - | - | - | - | - | X |
| browser | X | X | X | X | - | X | X |

`X` = denied, `-` = allowed

## Team Configurations

### Full Team (7 agents) — Recommended
All agents active. Best for multi-brand operations with high content volume.

### Lean Team (4 agents)
Leader + Content + Designer + Engineer. Suitable for single-brand or low-volume operations. Research handled by Leader; no independent review; no browser automation.

### Custom
Select any combination. Leader is always required.
