# NEAR Content Creator (OpenClaw Skill)

OpenClaw skill that generates NEAR-focused content in four formats:

- Educational threads (`near_content_thread`)
- Daily market updates (`near_content_update`)
- Ecosystem news digests (`near_content_news`)
- Tutorial content (`near_content_tutorial`)

## Install

```bash
npm install
```

## Build

```bash
npm run build
```

## Test

```bash
npm test
```

## Output formats

- `near_content_thread(topic)` -> `string[]`
- `near_content_update()` -> `string`
- `near_content_news()` -> `NewsItem[]`
- `near_content_tutorial(topic)` -> `string`

## Quality guardrails

- Thread output is always normalized to `1/8` ... `8/8`.
- Each thread line is kept within practical social-post length.
- News feed is deduplicated and ranked by source reliability + recency.
- Market update includes a data-quality line to show signal coverage.

## Publishing

Package metadata for MoltHub is in `molthub.json`.
