---
name: content-pipeline
description: Orchestrate full content workflow (planning→writing→design→publishing→tracking). Use when automating full content workflow from planning to publishing.
author: 무펭이 🐧
---

# content-pipeline

Meta skill orchestrating the entire content production flow.

## Pipeline Stages

```
1. seo-content-planner → Keyword analysis & content planning
2. copywriting → Write body text
3. cardnews → Generate card news images
4. social-publisher → Publish to Instagram/SNS
5. Performance tracking → Feedback via daily report
```

## Usage

### Full Auto-execution
```bash
content-pipeline --auto --topic "Photobooth usage tips"
```

### Individual Stage Execution
```bash
# Stage 1: Planning
content-pipeline --step plan --topic "Photobooth trends"

# Stage 2: Write body (auto-loads previous stage event)
content-pipeline --step write

# Stage 3: Generate card news
content-pipeline --step design

# Stage 4: Publish
content-pipeline --step publish

# Stage 5: Check performance
content-pipeline --step track
```

## Event Integration

Each stage automatically reads previous stage results from `events/` directory:

- `seo-plan-YYYY-MM-DD.json` → copywriting input
- `content-draft-YYYY-MM-DD.json` → cardnews input
- `content-published-YYYY-MM-DD.json` → daily-report input

## Options

- `--auto` — Auto-execute all stages
- `--step <plan|write|design|publish|track>` — Execute specific stage only
- `--topic <topic>` — Specify content topic
- `--skip-review` — Proceed without approval at each stage (risky)

## Execution Flow

### Auto Mode (`--auto`)
1. Execute seo-content-planner → Generate `events/seo-plan-YYYY-MM-DD.json`
2. Execute copywriting with generated keywords/topic → Generate `events/content-draft-YYYY-MM-DD.json`
3. Generate cardnews based on draft → Generate `events/cardnews-ready-YYYY-MM-DD.json`
4. Execute social-publisher with images + caption → Generate `events/content-published-YYYY-MM-DD.json`
5. Auto-include publishing results in daily-report

### Stage-by-stage Mode (`--step`)
Request approval at each stage:
- Review plan → approve → next
- Review draft → approve → next
- Preview card news → approve → publish

## Examples

### Generate Photobooth Tips Content
```bash
content-pipeline --auto --topic "Preserving wedding memories with photobooths"
```

Result:
- SEO keywords: "wedding photobooth", "wedding photo booth", etc.
- Blog draft 1200 chars
- Card news 5 slides (1024x1024 square)
- Auto-publish to Instagram (tag collaboration account)
- Include publishing results in daily report

### Manual Verification by Stage
```bash
# 1. Review plan first
content-pipeline --step plan --topic "University festival photobooths"
# → Generate events/seo-plan-2026-02-14.json

# 2. Write draft after reviewing plan
content-pipeline --step write
# → Generate events/content-draft-2026-02-14.json

# 3. Design after reviewing draft
content-pipeline --step design
# → Generate 5 card news slides

# 4. Publish after final review
content-pipeline --step publish
```

## Cautions

- `--auto` mode proceeds automatically through stages, so always verify content before final publish
- Images must be JPG format (PNG may cause Instagram errors)
- After publishing, `events/content-published-YYYY-MM-DD.json` automatically collected by daily-report

## Implementation Guide

As this is a meta skill, during actual implementation:
1. Check `events/seo-plan-*.json` → load if exists
2. If not exists, execute seo-content-planner
3. Pass results as input to next skill
4. Generate event file at each stage

---

**Author**: 무펭이 🐧  
**Created**: 2026-02-14  
**Status**: Production Ready
