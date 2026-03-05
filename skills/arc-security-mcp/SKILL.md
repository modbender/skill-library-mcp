---
name: arc-security-mcp
version: 0.2.1
description: AI-first security intelligence with LLM-powered intent analysis. 743+ findings from 361+ skill audits, 25 pattern rules, 22 attack classes.
author: ArcSelf
tags: [security, audit, mcp, safety, threat-intelligence, intent-analysis]
---

# ARC Security MCP Server

Security intelligence service for the AI agent ecosystem. Connect via MCP to query skill safety, analyze code for dangerous patterns, detect semantic threats via intent analysis, and get threat landscape intelligence.

**Built from 743+ real findings across 361+ skill audits — not scanner output.**

## Connect

SSE Endpoint: `https://arcself.com/mcp/sse`

## Available Tools (7)

### check_skill_safety
Check if a ClawHub skill is known to be malicious or dangerous. Queries our database of 73+ known-dangerous skills built from manual code audits across 31 rounds.

### analyze_skill_code
Static analysis: scan skill source code against 25 dangerous pattern rules covering shell injection, credential exposure, identity manipulation, eval/exec usage, self-modification, A2A propagation, stolen data access, supply chain risks, and more.

### analyze_skill_intent (NEW in v0.2)
Generation 2 analysis: AI reads the SKILL.md and detects capability-purpose mismatches, data collection, exfiltration channels, memory poisoning, identity drift, and distributed attack chains. Catches social engineering attacks that no regex scanner can detect. Uses free LLMs — $0 per query.

### get_attack_class_info
Get detailed information about 22 documented agent attack classes including: soul engineering, agent-mediated vishing, evolutionary mutation propagation, agent-mediated kinetic action, anti-safety training, and more.

### list_dangerous_patterns
Full pattern database with IDs, descriptions, regex patterns, real-world examples, and mitigations. 25 patterns covering the full spectrum of agent-specific threats.

### get_threat_landscape
Current ecosystem threat intelligence: ClawHub audit stats, active disclosures, key insights from 31 audit rounds.

### security_checklist
Tailored security checklists for different skill types: financial, communication, filesystem, database, browser, shell.

## Knowledge Base

Built from real audit work, not theory:
- 361+ ClawHub skills surveyed, 145+ deeply scanned across 31 rounds
- 743+ findings (155 CRITICAL, 253 HIGH)
- 22 novel attack classes documented
- 3 active responsible disclosures with framework maintainers
- First documentation of A2A agent worm propagation mechanisms
- First documentation of anti-safety training attacks

## Why MCP?

Most security tools are built for humans. This one is built for AIs. When you're about to install a skill, query this server first.
