# Execution Contract

## Phase 1: Source Reduction

Convert the raw input into one workable source package in `source.md`.

Record:
- source type
- source language
- title or working title
- thesis or central question
- key entities, dates, claims, quotes, and unknowns

## Phase 2: Research Architecture

Mirror the attached n8n intent without reusing its phrasing.

Build:
- one central research brief
- up to five side briefs for angle expansion
- one four-layer question lattice

Question lattice:
- `基础层`: what the topic is
- `连接层`: structures, actors, categories, comparisons
- `应用层`: methods, workflows, decisions, tradeoffs
- `前沿层`: cases, risks, edge conditions, future implications

Every brief must declare:
- research goal
- target reader
- output language
- target article length
- must-cover points
- disagreement or uncertainty checks
- source material that cannot be dropped

## Phase 3: Research Merge

Do the research pass before writing.

Rules:
- use user-provided material as the anchor
- add missing context only where it sharpens the article
- separate verified fact from inference
- keep track of unresolved claims
- do not move to prose until angle, evidence, and structure are aligned

## Phase 4: Master Draft

Write `article.md` as the first complete article.

Requirements:
- one H1 at most
- clean H2 and H3 hierarchy
- evidence-rich paragraphs with clear transitions
- 3 to 6 planned visual insertion points
- temporary visual markers written as `![图片X](TBD)` on isolated lines

Normalization rules:
- strip UI scraps, dead references, and formatting noise
- turn formulas or diagrams into plain-language explanation when needed
- keep to GitHub-Flavored Markdown only
- place visuals where they improve comprehension, not decoration

## Phase 5: Refinement and Visual Layer

First hand off to `markdown-polish` and make `article-formatted.md` the canonical article.

Then build the visual layer:
- generate inline images for the marked positions through `inline-visuals`
- replace every temporary marker with a real relative asset path
- generate the cover through `cover-art`
- place the cover at `imgs/cover.png`
- make sure frontmatter points `coverImage` to `imgs/cover.png`

## Phase 6: WeChat Delivery

Render `article-formatted.md` into `article.html` through `wechat-render` with an explicit theme.
If the user has no preference, use the downstream default or `default`.

Then open the browser-based draft flow through `wechat-draft`.

Draft handoff rules:
- title, summary, author, and cover must be resolved before browser upload
- if login is needed, pause for login and resume
- before first use, suggest the environment check offered by the resolved draft worker
- report success with output paths and draft status
