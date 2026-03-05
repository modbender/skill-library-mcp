---
description: Lint Markdown files for style issues, broken links, and formatting problems with auto-fix suggestions.
---

# Markdown Linter

Check and improve Markdown file quality with style checks and auto-fix.

**Use when** linting markdown files, checking link validity, or fixing formatting.

## Requirements

- Optional: `markdownlint-cli` (`npm install -g markdownlint-cli`)
- Works without external tools using text analysis
- No API keys needed

## Instructions

1. **Using markdownlint-cli** (preferred if available):
   ```bash
   # Lint a single file
   npx markdownlint README.md

   # Lint a directory
   npx markdownlint "docs/**/*.md"

   # Auto-fix issues
   npx markdownlint --fix README.md

   # With config file
   npx markdownlint -c .markdownlint.json README.md
   ```

2. **Manual analysis** (when CLI unavailable) — check for:

   | Issue | How to Detect | Fix |
   |-------|--------------|-----|
   | Skipped heading levels | `# → ###` (skipped `##`) | Add missing level |
   | Inconsistent list markers | Mixed `*`, `-`, `+` | Standardize to `-` |
   | Trailing whitespace | Lines ending with spaces | Trim trailing spaces |
   | Missing blank lines | No blank line before/after headings | Add blank lines |
   | Long lines | Lines > 120 chars | Wrap or restructure |
   | Broken relative links | `[text](./missing.md)` | Verify file exists |
   | Duplicate headings | Multiple `## Setup` sections | Make headings unique |
   | Missing alt text | `![](image.png)` | Add descriptive alt text |

3. **Link validation**:
   ```bash
   # Extract all links
   grep -oE '\[([^\]]*)\]\(([^)]+)\)' file.md

   # Check relative links exist
   grep -oE '\]\(\.\/[^)]+\)' file.md | sed 's/.*(\.\///' | sed 's/)//' | while read f; do
     [ ! -f "$f" ] && echo "BROKEN: $f"
   done
   ```

4. **TOC generation** (on request):
   ```bash
   # Extract headings and generate TOC
   grep -E '^#{1,3} ' file.md | sed 's/^## /  - /; s/^### /    - /; s/^# /- /'
   ```

5. **Output format**:
   ```
   ## 📝 Markdown Lint Report — README.md

   | Line | Issue | Severity |
   |------|-------|----------|
   | 12 | Heading level skipped (h1 → h3) | ⚠️ Warning |
   | 25 | Trailing whitespace | 🔵 Style |
   | 38 | Broken link: ./setup.md | 🔴 Error |

   **Summary:** 1 error, 1 warning, 1 style issue
   **Auto-fixable:** 1 of 3 issues
   ```

## Recommended .markdownlint.json

```json
{
  "MD013": { "line_length": 120 },
  "MD033": false,
  "MD041": false
}
```

## Edge Cases

- **MDX files**: Some JSX syntax will trigger false positives. Use `MD033: false` to allow HTML.
- **Generated files**: Skip auto-generated markdown (CHANGELOG.md, API docs).
- **Frontmatter**: Ensure linter is configured to ignore YAML frontmatter blocks.
- **Tables**: Long tables may trigger line-length warnings — consider disabling MD013 for those files.
