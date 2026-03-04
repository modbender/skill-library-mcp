---
name: research-paper-kb
description: "Persistent cross-session knowledge base for research papers. Ingest arXiv/DOI → extract method, gap, threat level → append to PAPERS.md. Never lose paper context again across sessions."
homepage: https://github.com/IlkhamFY/stch-botorch
metadata: {"author":"IlkhamFY","category":"Academic & Research","tags":["research","papers","arxiv","bibtex","knowledge-base","literature","academic","persistent-memory"]}
---

# research-paper-kb

**Persistent research paper knowledge base for AI agents.**

Ingest any paper (arXiv URL, DOI, or title) and extract structured intelligence into a permanent `PAPERS.md` knowledge base that survives across sessions. Never lose context on a paper again.

---

## Trigger Conditions

Use this skill when the user:
- Pastes an arXiv URL (e.g. `https://arxiv.org/abs/2310.12345`)
- Pastes a DOI (e.g. `10.1038/s41586-024-07156-8`)
- Says "add this paper to my KB" / "track this paper" / "save this paper"
- Says "what do we know about [paper title]"
- Says "update my paper KB" / "scan my PAPERS.md"
- Says "show me the papers I'm tracking" / "what papers have I saved"

---

## What This Skill Does

1. **Fetches** the paper abstract, metadata, and key sections
2. **Extracts** structured intelligence (method, gap, threat level, overlap)
3. **Generates** a clean BibTeX entry
4. **Appends** a structured entry to `PAPERS.md` in the workspace
5. **Updates** `MEMORY.md` with a pointer so future sessions know the KB exists
6. **Works across sessions** — the knowledge base is a file, not context

---

## Step-by-Step Instructions

### Step 1: Identify the Paper

Accept any of:
- arXiv URL: `https://arxiv.org/abs/XXXX.XXXXX`
- arXiv ID: `2310.12345` or `2310.12345v2`
- DOI: `10.XXXX/...`
- Title string: look up via Semantic Scholar API

**Normalize to arXiv ID or DOI** before proceeding.

### Step 2: Fetch Paper Metadata

**For arXiv papers** — fetch the abstract page:
```
https://arxiv.org/abs/<arxiv_id>
```
Extract: title, authors, date, abstract, subject categories.

Also fetch the Semantic Scholar API for structured metadata:
```
https://api.semanticscholar.org/graph/v1/paper/arXiv:<arxiv_id>?fields=title,authors,year,abstract,tldr,citationCount,influentialCitationCount,fieldsOfStudy
```

**For DOI papers** — use Semantic Scholar:
```
https://api.semanticscholar.org/graph/v1/paper/<DOI>?fields=title,authors,year,abstract,tldr,citationCount,influentialCitationCount,externalIds
```

**For title lookup:**
```
https://api.semanticscholar.org/graph/v1/paper/search?query=<url_encoded_title>&fields=title,authors,year,abstract,externalIds&limit=1
```

### Step 3: Extract Structured Intelligence

From the abstract and any available full text, extract:

| Field | What to Extract |
|-------|----------------|
| **Method** | Core technical approach or contribution (1-2 sentences) |
| **Gap they claim** | What problem/limitation they say they're solving |
| **Key results** | Main quantitative or qualitative outcome |
| **Overlap with user's work** | Ask the user if context is unclear; or infer from prior PAPERS.md entries and MEMORY.md |
| **Threat level** | 1-5 scale: how much does this threaten the user's research? (1=unrelated, 5=directly competing) |
| **Citation count** | From Semantic Scholar |
| **Related papers** | Up to 3 highly-cited related papers from the same fetch |

**Threat level guide:**
- 1 — Unrelated field, no overlap
- 2 — Adjacent method, different application
- 3 — Similar approach, different dataset/domain
- 4 — Direct competition, overlapping claims
- 5 — Near-identical work, same target problem

### Step 4: Generate BibTeX

Generate a clean BibTeX entry. Format:

**For arXiv:**
```bibtex
@article{<AuthorYEARkeyword>,
  title     = {<Full Title>},
  author    = {<Author1> and <Author2> and ...},
  journal   = {arXiv preprint arXiv:<id>},
  year      = {<year>},
  url       = {https://arxiv.org/abs/<id>},
  note      = {arXiv:<id>}
}
```

**For published paper:**
```bibtex
@article{<AuthorYEARkeyword>,
  title     = {<Full Title>},
  author    = {<Author1> and <Author2> and ...},
  journal   = {<venue>},
  year      = {<year>},
  doi       = {<doi>},
  url       = {https://doi.org/<doi>}
}
```

BibTeX key convention: `FirstAuthorLastNameYearFirstContentWord` (e.g., `Smith2024diffusion`)

### Step 5: Write to PAPERS.md

Check if `PAPERS.md` exists in the workspace root. If not, create it with the header:

```markdown
# PAPERS.md — Research Paper Knowledge Base
> Auto-maintained by the `research-paper-kb` skill. Add papers with: "add this paper to my KB"
> Last updated: <date>

---
```

**Append** (never overwrite) the following entry template:

```markdown
## [<Short Title>](<arxiv_or_doi_url>)
**Added:** <YYYY-MM-DD>  
**Authors:** <Author1>, <Author2>, ...  
**Venue:** <arXiv / Conference / Journal>  
**Citations:** <N> (Semantic Scholar)  
**Threat Level:** <1-5> — <one-line reason>

### Method
<1-2 sentence description of the core technical contribution>

### Gap They Claim
<What problem/limitation they say they're solving>

### Key Results
<Main outcomes, benchmarks, or claims>

### Overlap With My Work
<How this relates to the user's research — ask if unclear>

### Notes
<Any additional context the user provides, or leave blank>

### BibTeX
```bibtex
<bibtex entry>
```

---
```

### Step 6: Update MEMORY.md

After writing to PAPERS.md, append or update the PAPERS.md pointer in `MEMORY.md`:

Find or create a section `## Research Paper KB`:
```markdown
## Research Paper KB
- PAPERS.md exists in workspace root — <N> papers tracked as of <date>
- Latest addition: <Short title> (<threat level>/5)
- Run `research-paper-kb` to add more papers
```

If the section already exists, update the count and latest addition line.

### Step 7: Confirm to User

Reply with a summary:
```
✅ Added to PAPERS.md

**[Paper Title]** (<year>)
- Authors: ...
- Threat level: X/5 — <reason>
- BibTeX key: `AuthorYearWord`

PAPERS.md now has N papers. Run `show me my papers` to review.
```

---

## Query Mode: "Show Me My Papers"

When the user asks to review their paper KB:
1. Read `PAPERS.md`
2. Summarize: total count, highest threat-level papers, recently added
3. Optionally filter by threat level, topic, or year
4. Offer to export BibTeX for all papers: collect all `@article{...}` blocks and present as a code block

---

## Query Mode: "What Do We Know About X?"

When the user asks about a specific paper or topic:
1. Search `PAPERS.md` for matching title/author/keywords
2. Return the structured entry
3. If not found, offer to add it: "This paper isn't in your KB yet. Want me to add it?"

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| arXiv paper not found | Try Semantic Scholar title search; if still not found, ask user to confirm title |
| DOI behind paywall | Fetch abstract from DOI.org metadata (`https://doi.org/<doi>` with Accept: application/json); note "full text unavailable" |
| Paper already in PAPERS.md | Detect by title/arXiv ID match; offer to update notes or threat level instead |
| User doesn't know their research area | Ask: "What's your research focus? I'll use this to assess overlap." Store in MEMORY.md |
| Semantic Scholar rate limit | Fall back to arXiv API: `http://export.arxiv.org/api/query?id_list=<id>` |

---

## Integration With Other Skills

This skill works best alongside:
- **`citation-management`** — for full BibTeX workflow and PubMed/Google Scholar search
- **`biorxiv-database`** — for biology/life-science preprints (use to find papers to add)
- **`cs-research-methodology`** — for identifying gaps and research proposals from your KB
- **`proactive-research`** (ClaWHub) — can feed new papers into this KB automatically

---

## Files Modified

| File | Action |
|------|--------|
| `PAPERS.md` | Append new entry (create if missing) |
| `MEMORY.md` | Update `## Research Paper KB` section |

**Never modifies:** SOUL.md, USER.md, AGENTS.md, TOOLS.md, or any project files.

---

## Example Interaction

**User:** "Add this to my KB: https://arxiv.org/abs/2310.06825"

**Agent:**
1. Fetches arXiv 2310.06825 → "Mistral 7B" by Jiang et al.
2. Fetches Semantic Scholar metadata (12k citations)
3. Extracts: method = grouped-query attention + sliding window; gap = efficient 7B model
4. Assesses threat level vs user's work (reads MEMORY.md for context)
5. Generates BibTeX key `Jiang2023mistral`
6. Appends structured entry to PAPERS.md
7. Updates MEMORY.md
8. Replies: "✅ Added Mistral 7B (threat: 2/5 — efficient inference, different from your focus on X)"

---

## Metadata

```yaml
name: research-paper-kb
version: 1.0.0
author: <your-github-handle>
category: Academic & Research
tags: [research, papers, arxiv, bibtex, knowledge-base, literature, academic, persistent-memory]
summary: Persistent cross-session knowledge base for research papers. Ingest arXiv/DOI → extract method/gap/threat level → append to PAPERS.md. Never lose paper context again.
requires: []
```
