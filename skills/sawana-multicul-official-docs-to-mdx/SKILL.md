---
name: official-docs-to-mdx
description: Download and normalize official documentation pages into local .mdx files at user-specified paths using markdown.new. Use when user asks to fetch docs from a URL, archive official docs locally, sync docs snapshots, or convert docs pages into clean MDX with frontmatter (title, description, sourceUrl, retrievedAt).
---

# Official Docs to MDX

Convert a docs URL into a cleaned local `.mdx` file at a path the user specifies.
Use this skill when the user wants reproducible, file-based docs snapshots for local knowledge bases, RAG prep, or project docs folders.

## Quick Start

Run:

```bash
scripts/mdnew_to_mdx.sh <source_url> <output_mdx_path>
```

Example:

```bash
scripts/mdnew_to_mdx.sh \
  https://docs.convex.dev/agents/agent-usage \
  docs/convex/agent-usage.mdx
```

## Workflow

1. Validate inputs.
   - Require exactly 2 args: source URL and output path.
   - Keep URL as full `https://...` form.
2. Convert with script.
   - Execute `scripts/mdnew_to_mdx.sh`.
3. Confirm output.
   - Verify file exists.
   - Print or inspect frontmatter for `title`, `description`, `sourceUrl`, `retrievedAt`.
4. Add indexes for folder-based docs (required).
   - Any docs folder must include `index.mdx`.
   - If `docs/` exists, `docs/index.mdx` must exist.
   - Index files should link child docs/subfolders.
   - Keep frontmatter: `title`, `description`, `sourceUrl` (`local://...` allowed), `retrievedAt`.
5. Report result.
   - Return output path(s), overwrite status, and any created/updated index files.

## Output Contract

The generated MDX must include frontmatter:

- `title`
- `description`
- `sourceUrl`
- `retrievedAt` (UTC `YYYY-MM-DD`)

Body is cleaned to remove common docs-site artifacts and excess blank lines.

## Script Details

For behavior details and cleanup rules, read:

- `references/mdnew_to_mdx.md`

Use the bundled script directly:

- `scripts/mdnew_to_mdx.sh`

## Notes

- Dependencies: `bash`, `curl`, `awk`, `mktemp`.
- Output file is overwritten if it already exists.
- Re-run anytime to refresh docs snapshot from upstream.
