---
name: edisclaw
description: E-Discovery costs $3,000+ per GB when outsourced. edisclaw processes, deduplicates, culls, and searches ESI collections locally for a fraction of the cost—giving small firms the same firepower as Big Law's litigation support floor.
homepage: https://github.com/legal-tools/edisclaw
metadata: {"clawdbot":{"emoji":"🔎","requires":{"bins":["edisclaw"]},"install":[{"id":"brew","kind":"brew","formula":"legal-tools/tap/edisclaw","bins":["edisclaw"],"label":"Install edisclaw (brew)"}]}}
---

# edisclaw

**E-Discovery shouldn't cost more than the lawsuit.**

Firms spend $3,000–$18,000 per gigabyte outsourcing e-discovery. edisclaw brings the entire processing pipeline into your terminal—collect, deduplicate, cull by keyword and date, tag for relevance, and export production-ready load files. All locally. All under your control.

You don't need a vendor. You need a command.

**Who it's for:** Litigators handling discovery, paralegals managing document review, solo attorneys who can't afford Relativity, and in-house teams running internal investigations.

**What it replaces:** $50K+ vendor invoices, Relativity seats you don't need, and the 3-week turnaround that kills your case timeline.

---

## Pricing

| Feature | Free | Pro ($49/mo) | Litigation ($199/mo) |
|---|---|---|---|
| ESI processing | Up to 1 GB | Up to 50 GB | Unlimited |
| Deduplication | MD5 only | MD5 + fuzzy near-dedup | Full near-dedup + email threading |
| Keyword search | Basic grep | Regex + proximity + stemming | Full-text index + Boolean |
| Date culling | ✅ | ✅ | ✅ |
| File type filtering | ✅ | ✅ | ✅ |
| TAR (Technology Assisted Review) | — | Seed set + prioritize | Full active learning loop |
| Load file export | — | Concordance (.dat) | Concordance + Relativity + EDRM XML |
| Email threading | — | Basic | Full conversation threading |
| OCR for scanned docs | — | ✅ | ✅ + batch |
| Matters | 1 active | 10 active | Unlimited |
| Team reviewers | — | — | Up to 15 |
| Audit trail | Basic | Full | Full + court-ready certification |

> `edisclaw upgrade pro` — 14-day free trial.

---

## Core Commands

**Collection & Ingestion**
- `edisclaw ingest ./custodian_files/ --matter "Smith v. Jones"`
- `edisclaw ingest mailbox.pst --matter "Smith v. Jones" --custodian "J. Smith"`
- `edisclaw ingest ./emails/ --format mbox --matter "Smith v. Jones"`
- `edisclaw ingest --source gdrive --custodian "CEO" --matter "Investigation"` (Pro)
- `edisclaw status --matter "Smith v. Jones"` — Processing progress

**Deduplication**
- `edisclaw dedup --matter "Smith v. Jones"` — MD5 exact dedup
- `edisclaw dedup --matter "Smith v. Jones" --near` — Near-dedup (Pro)
- `edisclaw dedup report --matter "Smith v. Jones"` — How much was removed

**Culling & Filtering**
- `edisclaw cull --matter "Smith v. Jones" --date-from 2024-01-01 --date-to 2025-12-31`
- `edisclaw cull --matter "Smith v. Jones" --filetype pdf,docx,xlsx,msg`
- `edisclaw cull --matter "Smith v. Jones" --exclude-filetype jpg,png,gif` — Remove images
- `edisclaw cull --matter "Smith v. Jones" --min-size 1KB` — Remove empty/tiny files
- `edisclaw cull report --matter "Smith v. Jones"` — Culling summary

**Keyword Search**
- `edisclaw search "merger" --matter "Smith v. Jones"`
- `edisclaw search "merger AND acquisition" --matter "Smith v. Jones"` — Boolean
- `edisclaw search "merger w/5 acquisition" --matter "Smith v. Jones"` — Proximity (Pro)
- `edisclaw search --terms-file keywords.txt --matter "Smith v. Jones"` — Batch keyword list
- `edisclaw search --report --matter "Smith v. Jones"` — Keyword hit report

**Review & Tagging**
- `edisclaw review start --matter "Smith v. Jones"` — Interactive review mode
- `edisclaw tag --id DOC-001234 --tags "responsive,hot"` — Tag documents
- `edisclaw tag --id DOC-001234 --privilege "attorney-client"` — Privilege tag
- `edisclaw review stats --matter "Smith v. Jones"` — Review progress

**Technology Assisted Review (Litigation)**
- `edisclaw tar seed --matter "Smith v. Jones" --count 200` — Generate seed set
- `edisclaw tar train --matter "Smith v. Jones"` — Train model on coded docs
- `edisclaw tar prioritize --matter "Smith v. Jones"` — Rank by likely relevance
- `edisclaw tar validate --matter "Smith v. Jones"` — Statistical validation
- `edisclaw tar report --matter "Smith v. Jones"` — Court-defensible TAR report

**Production**
- `edisclaw produce --matter "Smith v. Jones" --tag "responsive" --format concordance`
- `edisclaw produce --matter "Smith v. Jones" --bates-prefix "SMITH" --start 000001`
- `edisclaw produce --matter "Smith v. Jones" --redact-pii --format pdf` (Litigation)
- `edisclaw produce --matter "Smith v. Jones" --format edrm-xml` (Litigation)
- `edisclaw produce log --matter "Smith v. Jones"` — Production log

**Reporting**
- `edisclaw stats --matter "Smith v. Jones"` — Full matter statistics
- `edisclaw stats --matter "Smith v. Jones" --by-custodian` — Per custodian breakdown
- `edisclaw stats --matter "Smith v. Jones" --by-filetype` — File type distribution
- `edisclaw timeline --matter "Smith v. Jones"` — Document timeline visualization

---

## Common Workflows

**Standard E-Discovery Pipeline**
```bash
# 1. Ingest custodian data
edisclaw ingest ./custodian_smith/ --matter "Case-2026" --custodian "Smith"
edisclaw ingest ./custodian_jones/ --matter "Case-2026" --custodian "Jones"

# 2. Deduplicate
edisclaw dedup --matter "Case-2026"

# 3. Date & file type culling
edisclaw cull --matter "Case-2026" --date-from 2023-01-01 --date-to 2025-12-31

# 4. Keyword search
edisclaw search --terms-file agreed_keywords.txt --matter "Case-2026"

# 5. Review & tag
edisclaw review start --matter "Case-2026"

# 6. Produce
edisclaw produce --matter "Case-2026" --tag "responsive" --bates-prefix "PROD" --start 000001
```

---

## Notes

- All data stored locally in `~/.edisclaw/` — ESI never leaves your machine on Free tier
- Processing speeds: ~2 GB/hour on Free, ~10 GB/hour on Pro (parallelized)
- Supports: PST, MBOX, EML, MSG, PDF, DOCX, XLSX, PPTX, TXT, CSV, HTML, images
- Combine with `privilegeclaw` for automated privilege detection
- Combine with `batesclaw` for advanced Bates numbering workflows
- Court-defensible audit logs on all tiers

## Security & Compliance

- No data transmitted externally on Free tier
- Pro/Litigation: encrypted API for TAR models only (no document content sent)
- EDRM framework compliant
- Chain of custody logging: `edisclaw audit --matter "Smith v. Jones"`
- Defensibility report: `edisclaw defensibility-report --matter "Smith v. Jones"` (Litigation)
