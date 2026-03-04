---
name: paper-notion-summarizer
description: Fetch paper metadata by title or arXiv/DOI link, create a deep structured summary, and post it as a Notion page. The agent reads the paper and writes a seminar-quality summary adapted to the user's language.
---

# Paper Notion Summarizer

## Purpose

Given a paper title or arXiv link, create a **seminar-quality, deeply structured summary** and upload it to Notion.

> ⚠️ This is NOT an extractive summary. The **agent reads the full paper and writes an original analysis**.

## Language Adaptation

**Write the summary in the same language as the user's request.**
- If the user writes in Korean → write in Korean (technical terms in English)
- If the user writes in English → write in English
- If the user writes in Japanese → write in Japanese
- And so on for any language.

Section headings in the summary JSON should match the user's language. The English template below is the canonical structure — adapt headings to the user's language.

## Workflow (3 phases)

### Phase 1: Extract paper content

```bash
python3 scripts/extract_paper.py \
  --output /tmp/paper_extract.json \
  "https://arxiv.org/abs/2301.12345"
```

Or by title:
```bash
python3 scripts/extract_paper.py \
  --output /tmp/paper_extract.json \
  --title "Attention Is All You Need"
```

Options:
- `--output`, `-o`: Output file path (defaults to stdout)
- `--skip-fulltext`: Extract abstract only (fast mode, skip PDF)
- `--doi`: Explicit DOI
- `--arxiv-id`: Explicit arXiv ID

### Phase 2: Agent reads and writes the summary

Read the extracted JSON section by section (`read` tool with `offset`/`limit` for large files), then write a structured summary JSON to `/tmp/paper_summary.json`.

#### Reading strategy (context management)
- Read Abstract → Introduction → Method → Experiments → Conclusion in order
- For long papers, read in chunks and accumulate understanding
- Focus on: core idea, key equations, experimental setup, main results, ablations

#### Summary JSON template

```json
{
  "title": "Paper Title (original language)",
  "metadata": {
    "authors": "Author list",
    "year": "2024",
    "venue": "NeurIPS 2024",
    "doi": "10.xxxx/xxxxx",
    "url": "https://arxiv.org/abs/xxxx.xxxxx",
    "source": "arXiv"
  },
  "sections": [
    {
      "heading": "0. Metadata",
      "content": "- Authors: ...\n- Year: ...\n- Venue: ...\n- Code: ..."
    },
    {
      "heading": "1. One-line Summary",
      "content": "What this paper does in one sentence."
    },
    {
      "heading": "2. Problem & Motivation",
      "content": "- What problem does it solve?\n- Why are existing methods insufficient?\n- Why is this research needed?"
    },
    {
      "heading": "3. Key Contributions",
      "content": "1. First contribution\n2. Second contribution\n3. Third contribution"
    },
    {
      "heading": "4. Method",
      "content": "Detailed pipeline/architecture description.\nCore ideas, key equations included.\n\n### Core Idea\n...\n\n### Architecture\n...\n\n### Training\n...\n\n### Key Equations\n$$equation$$"
    },
    {
      "heading": "5. Experiments",
      "content": "### Setup\n- Datasets: ...\n- Baselines: ...\n- Metrics: ...\n\n### Main Results\n- Key numbers and comparisons\n- Where it works and where it doesn't"
    },
    {
      "heading": "6. Ablation & Analysis",
      "content": "- Per-component contributions\n- Interesting analysis results\n- Hyperparameter sensitivity"
    },
    {
      "heading": "7. Limitations & Future Work",
      "content": "- Author-acknowledged limitations\n- Additional limitations you identify\n- Future research directions"
    },
    {
      "heading": "8. Overall Assessment",
      "content": "- Research significance\n- Strengths and weaknesses\n- Connections to related work\n- Ideas applicable to user's research"
    }
  ]
}
```

#### Quality guidelines

1. **Terminology**: Keep technical terms in their original language; explanations in the user's language.
2. **Equations**: Include key equations in LaTeX (`$$ ... $$`).
3. **Depth**: Seminar-presentation level understanding.
   - Method: Not just "they did X" but "why they designed it this way, what each component does"
   - Experiments: Not just "it worked" but "X% improvement over Y baseline under Z conditions"
4. **Critical perspective**: Record limitations and open questions, not just strengths.
5. **Connections**: If you know the user's research interests, connect the paper to them.
6. **No programming code blocks**: Do NOT use fenced code blocks (``` ```) in `sections[*].content`. Math expressions (`$$ ... $$`, `` ```latex ``) are allowed.
7. **No emoji in headings**: Use numbered prefixes: `0. Metadata`, `1. One-line Summary`, etc.

### Phase 3: Push to Notion

```bash
python3 scripts/push_to_notion.py \
  /tmp/paper_summary.json \
  --parent-page-id YOUR_PAGE_ID
```

Options:
- `--parent-page-id`: Notion page ID to create the summary under
- `--force-update`: Overwrite existing page with same title
- `--dry-run`: Preview without uploading
- `--notion-key`: Explicit Notion API token

## Quick Start (full agent flow)

```
1. python3 scripts/extract_paper.py -o /tmp/paper_extract.json "https://arxiv.org/abs/..."
2. read /tmp/paper_extract.json (section by section)
3. Write summary → /tmp/paper_summary.json
4. python3 scripts/push_to_notion.py /tmp/paper_summary.json --parent-page-id PAGE_ID
```

## Configuration

| Config | Source | Description |
|--------|--------|-------------|
| Notion API key | `NOTION_API_KEY` env or `~/.config/notion/api_key` | Required for Notion upload |
| Parent page | `NOTION_PARENT_PAGE_ID` env or `--parent-page-id` | Notion page to create summaries under |

## Notes

- arXiv papers use PDF extraction (requires `pypdf`). Install: `pip install pypdf`
- For very long papers (>100 pages), use `--skip-fulltext` and read HTML via `web_fetch`.
- Notion API version: `2025-09-03`
- The `extract_paper.py` script does NOT require a Notion API key — it only fetches and extracts.
