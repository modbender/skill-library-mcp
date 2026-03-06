---
name: literature-manager
description: Search, download, convert, organize, and audit academic literature collections. Use when asked to find papers, build a literature library, add papers to references, download PDFs, convert papers to markdown, organize references by category, audit a reference collection, or collect code/dataset links for tools mentioned in papers.
---

# Literature Manager

Manage academic literature collections: search → download → convert → organize → verify.

## Dependencies

- `pdftotext` (poppler-utils) — PDF text extraction
- `curl` — downloading
- `python3` — JSON processing in audit
- `file` (coreutils) — PDF validation
- `uvx markitdown[pdf]` (optional) — fallback PDF→MD converter (note: plain `uvx markitdown` does NOT work for PDFs — must use `uvx markitdown[pdf]`)

## Quick Start

```bash
# Download a single paper by DOI
bash scripts/download.sh "10.1038/s41592-024-02200-1" output_dir/

# Convert PDF to markdown
bash scripts/convert.sh paper.pdf output.md

# Verify a single PDF+MD pair
bash scripts/verify.sh paper.pdf paper.md

# Full audit of a references/ folder
bash scripts/audit.sh /path/to/references/
```

## Workflow

### 1. Search

Use `web_fetch` on Google Scholar:
```
https://scholar.google.com/scholar?q=QUERY&as_ylo=YEAR
```
Extract: title, authors, year, journal, DOI, PDF links.

For each result, identify the best open-access PDF source (see Download Strategy).

### 2. Download

Run `scripts/download.sh <DOI_or_URL> <output_dir/>` per paper. The script tries sources in order:
1. Direct publisher PDF (Nature, eLife, Frontiers, PNAS, bioRxiv, arXiv)
2. EuropePMC (`PMC_ID` → PDF)
3. bioRxiv/arXiv preprint
4. **Sci-Hub** — `https://sci-hub.box/<DOI>` (use when publisher is paywalled)

```bash
# Sci-Hub download example:
curl -L "https://sci-hub.box/10.1038/nature12345" -o paper.pdf
```

> ⚠️ **Legal note:** Sci-Hub may violate publisher terms of service or copyright law in some jurisdictions. Use only if you understand and accept the legal implications in your context.

If all sources fail (including Sci-Hub), flag as permanent paywall. Provide the user with the DOI and ask for manual download.

### 3. Convert

Run `scripts/convert.sh <input.pdf> <output.md>`. Uses `pdftotext` (reliable) with `uvx markitdown[pdf]` as fallback.

```bash
# Correct markitdown command for PDFs:
uvx markitdown[pdf] input.pdf > output.md

# ⚠️ The following will NOT work for PDFs (missing [pdf] extra):
# uvx markitdown input.pdf
```

Prefer `uvx markitdown[pdf]` over `pdftotext` when full fidelity (tables, figures captions) matters.

### 4. Organize

Standard folder structure:
```
references/
├── README.md              # Human index (summaries per category)
├── index.json             # Machine index (structured metadata)
├── RESOURCES.md           # Code repos + datasets
├── resources.json         # Structured version
├── <category-1>/
│   ├── papers/            # PDFs
│   └── markdown/          # Converted text
└── <category-N>/
    ├── papers/
    └── markdown/
```

Categories are user-defined. Number-prefix for sort order (e.g., `01-theoretical-frameworks/`).

#### index.json schema per paper
```json
{
  "id": "short_id",
  "title": "Full title",
  "authors": ["Author1", "Author2"],
  "year": 2024,
  "journal": "Journal Name",
  "doi": "10.xxxx/...",
  "category": "category_name",
  "subcategory": "optional",
  "pdf_path": "category/papers/filename.pdf",
  "markdown_path": "category/markdown/filename.md",
  "tags": ["tag1", "tag2"],
  "one_line_summary": "English one-liner",
  "key_concepts": ["concept1"],
  "relevance_to_project": "English description"
}
```

#### README.md pattern
Per category section, per paper: title, authors, year, journal, DOI, short summary in user's language.

### 4b. DOI-Based Filenames & Path Mapping

Downloaded files are often named using DOI format rather than `AuthorYear`:
```
10-1038_ncomms3018.md        # DOI: 10.1038/ncomms3018
10-1016_j-neuron-2015-03-034.md
```

When `markdown_path` entries in `index.json` become stale (e.g., after folder reorganization), maintain a separate mapping file:

```json
// temp/paper_md_mapping.json
{
  "author2024_keyword": "references/new-downloads/10-1038_s41592-024-02200-1.md",
  ...
}
```

To build this mapping: cross-reference each paper's DOI in `index.json` against actual files on disk. Use `find` + Python to automate.

#### index.json Known Pitfalls

- **`id: null` corruption**: If many entries have `id=null` and share the same `pdf_path`, the index was likely corrupted during a batch write. Rebuild from actual files on disk.
- **DOI errors**: Verify DOIs resolve correctly — typos in DOI fields are common (e.g., wrong suffix digits). Always cross-check with publisher page.
- **Dead `markdown_path`**: After restructuring folders, `markdown_path` in index.json often points to old locations. Use the mapping file above as the source of truth.

### 5. Verify

Run `scripts/audit.sh <references_dir/>` for full verification:
- Every PDF is valid (`file -b` = PDF)
- Every PDF title matches filename (`pdftotext | head`)
- Every PDF has matching markdown (and vice versa)
- index.json is valid, complete, paths exist, no duplicate IDs
- README.md stats match actual counts

### 6. Collect Resources

For tool/method papers, find GitHub repos and public datasets. Store in `RESOURCES.md` + `resources.json`.

## Sub-agent Strategy

For large batches, parallelize:
- **Download**: 1 sub-agent per batch of ~5-8 papers
- **Organize**: 1 sub-agent to build indexes
- **Verify**: 1 independent sub-agent (never the same as organizer)

Always use a separate sub-agent for verification (QC should not self-grade).

### ⚠️ Sub-agent Rules (Learned from Practice)

1. **One batch at a time** — do not spawn multiple note-writing batches simultaneously; LLM rate limits will cause silent failures
2. **Set a cron monitor whenever spawning long-running agents** — agents can fail silently without triggering auto-announce; cron catches this
3. **Cron monitor pattern:**
   ```
   1. Spawn agent(s)
   2. Immediately set a cron job (every 10-15 min, isolated agentTurn)
      → Check if expected output files exist
      → Re-spawn failed agents
      → When all complete: announce + delete cron
   3. After task finishes, confirm cron was removed
   ```

## Adding Papers Incrementally

To add papers to an existing collection:
1. Download + convert new papers into correct category folder
2. Append entries to index.json
3. Update README.md stats
4. Run audit to verify consistency
