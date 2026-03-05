---
name: research-to-wechat
description: An end-to-end WeChat article orchestrator that turns a keyword, article, URL, or video transcript into a researched article with a chosen voice, polished Markdown, inline visuals, cover image, WeChat-ready HTML, and a browser-saved draft. Use when the user wants 深度研究、写作、排版、配图、HTML 转换、或公众号草稿生成.
---

# Research to WeChat

Use this skill as a coordinator. Do not duplicate downstream skill wording.

## Core Rules

- Match the user's language.
- Ask one question at a time.
- Ask only when the answer changes source interpretation, style fidelity, or draft publishing behavior.
- Keep Markdown as the canonical article asset until the HTML handoff.
- Save a draft only. Never publish live.

## Capability Aliases

Resolve capabilities through internal aliases, not vendor-style names:
- `source-ingest`
- `markdown-polish`
- `inline-visuals`
- `cover-art`
- `wechat-render`
- `wechat-draft`

Use the current alias map in [capability-map.md](references/capability-map.md).

## Accepted Inputs

- keyword or topic phrase
- article text
- markdown file
- article URL
- video URL
- transcript, subtitles, notes, or summary

Video policy:
- first attempt source recovery from the page
- if only metadata is available, state the reduced research confidence
- if no usable transcript or notes exist, ask for transcript, subtitles, or key points

## Output

Create one workspace per article:
`research-to-wechat/YYYY-MM-DD-<slug>/`

Required assets:
- `source.md`
- `article.md`
- `article-formatted.md`
- `article.html`
- `imgs/cover.png`
- inline illustration files referenced by the markdown body

Required frontmatter in final markdown:
- `title`
- `author`
- `description`
- `coverImage`
- `styleMode`
- `sourceType`

## Style Resolution

Resolve style in this order:
1. explicit user instruction
2. preset mode
3. author mode
4. custom brief

Use the full style system in [style-engine.md](references/style-engine.md).

## Execution

Run the article through these phases:
1. source reduction
2. research architecture
3. research merge
4. master draft
5. refinement and visual layer
6. WeChat delivery

Use the execution contract in [execution-contract.md](references/execution-contract.md).

## Done Condition

The skill is complete only when all of these hold:
- the article reads as researched before it reads as polished
- the chosen style is visible without collapsing into imitation
- every visual adds narrative or explanatory value
- markdown and HTML agree on title, summary, cover, and image paths
- the workflow can stop safely at the highest-quality completed artifact if a later handoff fails
