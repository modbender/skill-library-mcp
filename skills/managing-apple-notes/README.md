# ClawHub Skill for inotes

This directory contains the ClawHub skill package for publishing to https://clawhub.ai

## Files

- `SKILL.md` - Main skill definition with metadata and instructions

## How to publish

### 1. Package the skill

```bash
cd /Users/dxm/Documents/walker/inotes
zip -r inotes-clawhub-skill.zip clawhub/SKILL.md
```

### 2. Upload to ClawHub

Visit https://clawhub.ai/upload and upload the zip file.

Or update existing skill with new version.

## Version tracking

Keep this SKILL.md in sync with the project version. Update when:
- New commands are added
- Installation instructions change
- Major bug fixes that affect usage

## Current version

Skill last updated for inotes v0.1.2 (2026-02-11)
