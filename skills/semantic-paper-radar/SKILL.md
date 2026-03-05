---
name: semantic-paper-radar
description: Semantic literature discovery and synthesis across arXiv/OpenAlex/PubMed (and optional Google Scholar adapters). Use when users ask for domain must-read papers, research trend mapping, paper recommendations, reading lists, or academic lineage/context for a topic in natural science, AI, engineering, medicine, or interdisciplinary research.
---

# Semantic Paper Radar

Build a domain reading list from natural-language intent, then output a concise research map.

## Workflow

1. Clarify query intent in one line:
   - topic + scope + time window + priority (`foundational` / `frontier` / `balanced`).
2. Run aggregated retrieval:
   - General: `python3 scripts/paper_radar.py search --query "<topic>" --max 40 --years 8`
   - Biomedical force-on: `python3 scripts/paper_radar.py search --query "<topic>" --max 40 --years 8 --biomed`
3. Generate synthesis report:
   - `python3 scripts/paper_radar.py report --query "<topic>" --max 40 --years 8 --top 12 --mode balanced`
   - Biomedical force-on: add `--biomed`
   - Export clickable HTML: add `--export-html` (optional `--html-out <path>`)

4. Present results in Chinese unless user asked otherwise:
   - 必读文献（分层）
   - 学术脉络（时间线）
   - 阅读顺序（先读3篇）
   - 可选下一步（细分子方向）

## Output Rules

- Prefer OpenAlex entries with DOI/citation metadata for "经典" judgement.
- Keep arXiv entries for "最新前沿" and unreviewed but high-momentum work.
- If the query is biomedical/clinical, explicitly include a caution that arXiv papers may be preprint.
- If retrieval is sparse, broaden query with synonyms and rerun once.

## Recommended Prompt Pattern

Use this framing when user asks for recommendations:

- "按 `经典奠基(3-5)` + `方法跃迁(3-5)` + `近两年新进展(3-5)` 输出"
- "每篇给：一句贡献、为什么必读、适合第几步读"
- "最后给该领域 3 条学术脉络主线"

## Optional Scholar Integration

If the environment already has a Scholar-capable tool/skill (e.g., serper-scholar), call it after `report` and use it only for:
- citation cross-check
- venue/author authority补充

Do not block core workflow if Scholar integration is unavailable.
