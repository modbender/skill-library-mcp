---
name: gh-extract
description: Extract content from a GitHub url.
metadata: {"openclaw":{"always":false,"emoji":"🦞","homepage":"https://clawhub.ai/guoqiao/gh-extract","os":["darwin","linux","win32"],"requires":{"bins":["uv"]}}}
triggers:
- "/gh-extract <url>"
- "Extract content form this github url"
- "Download this github file"
---

# GitHub Extract

Extract content from a GitHub url.

Use this skill when the user types `/gh-extract` or asks to extract/download/summarize a GitHub url.

## What it does
- Accepts an GitHub url, could be repo/tree/blob.
- Convert the url to github raw url.
- Extract file content from the raw url or save to a temp path.

## Requirements

- `uv`
- `wget`

## Usage

```bash
# print file content to stdout
uv run --script ${baseDir}/gh_extract.py <url>

# save file to a temp path, with a proper filename
uv run --script ${baseDir}/gh_extract.py <url> --save
```

## Notes
- only works for public repo.
- url can be repo/tree/blob
- for repo/tree, will try to get `README.md` or `SKILL.md` or `README.txt`
