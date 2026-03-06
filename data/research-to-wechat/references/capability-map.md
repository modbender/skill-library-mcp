# Capability Map

Use this file to resolve neutral capability aliases to installed skills without hardcoding vendor-style identifiers.

## Resolution Table

- `source-ingest`
  look for: a skill that fetches a URL and converts the page into markdown
  use for: article URLs, video URLs, login-gated pages, delayed-render pages
  note: prefer a worker that supports a wait mode for manual login or delayed loading

- `markdown-polish`
  look for: a skill that cleans markdown, repairs typography, and improves frontmatter and readability
  use for: canonical article cleanup before visuals and HTML rendering

- `inline-visuals`
  look for: a skill that analyzes article structure and inserts or generates visuals for body sections
  use for: informational or narrative images placed inside the article body

- `cover-art`
  look for: a skill that generates an article cover image from text content
  use for: producing `imgs/cover.png`

- `wechat-render`
  look for: a skill that converts markdown into WeChat-compatible HTML
  use for: rendering the canonical markdown article into `article.html`

- `wechat-draft`
  look for: a skill that opens the WeChat Official Account browser flow and saves an article draft
  use for: browser-based draft creation
  note: prefer a worker that supports draft saving rather than live publishing

## Loading Rule

- Do not load every implementation at once.
- Run `openskills list` when resolution is needed.
- Select the worker whose description best matches the alias requirement.
- Keep this skill as the control plane and the resolved skill as the worker.
