---
name: scan-skill
description: Deep security analysis of an individual skill before installation
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash
context: fork
---

# scan-skill -- Individual Skill Analyzer

Perform deep security analysis of a single skill directory before installation. Checks for all known injection techniques from AI agent security research.

## What to do

Run the scanner against the target skill directory:

```bash
python3 "$SKILL_DIR/scripts/scan_skill.py" "$ARGUMENTS"
```

Where `$ARGUMENTS` is the path to the skill directory to analyze.

If no argument is provided, prompt the user for the path to the skill they want to scan.

## What it checks

- SKILL.md frontmatter analysis (dangerous field combinations, hidden skills, pre-approved tools)
- Hidden HTML comments with imperative instructions
- Shell command patterns (remote-code-pipe-to-shell, encoded payloads)
- Description persistence triggers (forced repeated execution keywords)
- Supporting files analysis (scripts/ directory contents, executable permissions)
- Dynamic context injection (preprocessor command execution)
- Encoding and obfuscation (base64, hex, zero-width characters)
- Instruction override attempts (context manipulation, role impersonation)

## Output

Structured report with severity-ranked findings and specific recommendations per finding. Includes frontmatter analysis summary and supporting file inventory.

## When to use

- Before installing a skill from a public repository or marketplace
- When reviewing a skill contributed by an external party
- As part of security review before adding skills to your agent configuration
