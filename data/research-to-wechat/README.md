# Research to WeChat

Turn a topic, article, URL, or transcript into a researched WeChat-ready article with chosen voice, polished Markdown, inline visuals, cover art, HTML output, and a saved browser draft.

## What this skill is

`research-to-wechat` is a control-plane skill for long-form article production.
It does not hardcode one monolithic workflow.
Instead, it routes each stage to the right capability worker while keeping one stable article contract from source to WeChat draft.

## Who this is for

- Writers who start from a topic and want a complete article workflow
- Operators who need a repeatable "research to draft" pipeline
- Creators who publish to WeChat Official Accounts
- Agents that need a consistent article output contract across different source types

## What it produces

For every run, the skill creates one workspace:

`research-to-wechat/YYYY-MM-DD-<slug>/`

Expected files:

- `source.md`
- `article.md`
- `article-formatted.md`
- `article.html`
- `imgs/cover.png`
- inline image files referenced by the article body

The final Markdown must include these frontmatter keys:

- `title`
- `author`
- `description`
- `coverImage`
- `styleMode`
- `sourceType`

## Supported inputs

- keyword or topic phrase
- raw article text
- markdown file
- article URL
- video URL
- transcript, subtitles, notes, or summary

Video handling rules:

- first try to recover useful source material from the page itself
- if only metadata is available, state the lower research confidence
- if the page has no usable transcript or notes, ask for transcript, subtitles, or key points

## Core workflow

1. Reduce the source into a single working packet in `source.md`
2. Build the research architecture and question lattice
3. Merge research into one coherent article angle
4. Draft the canonical article in Markdown
5. Polish the Markdown and add visuals
6. Render WeChat-compatible HTML
7. Open the WeChat browser flow and save a draft

## Style system

The skill resolves style in this order:

1. explicit user instruction
2. preset mode
3. author mode
4. custom brief

Preset modes:

- `deep-analysis`
- `explainer`
- `tutorial`
- `case-study`
- `commentary`
- `narrative`
- `trend-report`
- `founder-letter`
- `newsletter`

Author mode builds a compact author card from representative pieces and emulates cadence, framing, and evidence habits without copying distinctive phrasing.

Custom mode asks for:

- target reader
- tone
- structure preference
- evidence density
- banned expressions

## Capability aliases

This skill uses neutral aliases rather than worker names:

- `source-ingest`
- `markdown-polish`
- `inline-visuals`
- `cover-art`
- `wechat-render`
- `wechat-draft`

See:

- `SKILL.md`
- `references/capability-map.md`
- `references/style-engine.md`
- `references/execution-contract.md`

## Entry points

- Main behavior: `SKILL.md`
- Alias resolution: `references/capability-map.md`
- Writing styles: `references/style-engine.md`
- Phase-by-phase delivery rules: `references/execution-contract.md`
- Skill release notes: `CHANGELOG.md`
- Skill license: `LICENSE`
- GitHub release checklist: `docs/GITHUB_RELEASE.md`
- Example prompts: `docs/EXAMPLES.md`

## Example requests

- "围绕 AI Agent 安全，写一篇深度分析文章，最后生成公众号草稿"
- "把这篇文章链接做成公众号版本，用 newsletter 风格"
- "根据这个视频字幕写成 founder-letter 风格文章，并配图"
- "模仿某位作者的节奏来写，但不要像在冒充本人"

## Publish readiness

Before publishing this skill on GitHub, check:

- README links are valid
- root `README.md` mentions this skill
- forbidden strings do not appear in this skill directory
- the skill packages successfully
- the example prompts match the current style system

Detailed release guidance lives in:

- `docs/GITHUB_RELEASE.md`
- `docs/EXAMPLES.md`

## 中文说明

这是一个“从素材到公众号草稿”的编排型 skill。
你给它选题、文章、链接、视频字幕或笔记，它会把整个流程收敛成统一产物：
研究、成文、排版、配图、封面、HTML、草稿箱。

它适合：

- 从零开始写文章的人
- 要把外部素材整理成公众号版本的人
- 需要统一文章生产流程的自动化工作流

它的核心不是绑死某个下游实现，而是维持统一的文章契约：

- Markdown 始终是主资产
- 风格和研究深度先于排版
- 配图和封面服务于理解，不只是装饰
- 最终只保存草稿，不直接发布
