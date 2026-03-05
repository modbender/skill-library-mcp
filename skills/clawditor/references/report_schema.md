# Clawditor Report Schema

Use this reference to keep output consistent and comparable across runs.

## exec_summary.md (template)
- Overall score: NN (Memory NN, Retrieval NN, Productive NN, Quality NN, Focus NN)
- Claw-to-claw delta: +N or -N (if prior eval exists)
- 10 bullets total:
  - Strongest wins (2-3)
  - Biggest bottlenecks (2-3)
  - Top 3 interventions (3)
  - Any standout risk (1-2)

## scorecard.md (template)
| Category | Score | Evidence | Rationale |
| --- | --- | --- | --- |
| Memory Health | NN | memory/INDEX.md | Short justification |
| Retrieval & Context Efficiency | NN | logs/... | Short justification |
| Productive Output | NN | git stats / artifacts | Short justification |
| Quality / Reliability | NN | logs / tests | Short justification |
| Focus / Alignment | NN | memory + logs | Short justification |

Top evidence section:
- Path: short snippet (no secrets)

## latest_report.json (schema)
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "workspace": {
    "path": "/path/to/workspace",
    "hash_or_git_head": "<git head or hash>"
  },
  "scores": {
    "overall": 0,
    "memory": 0,
    "retrieval": 0,
    "productive": 0,
    "quality": 0,
    "focus": 0
  },
  "deltas_vs_previous": {
    "overall": 0,
    "memory": 0,
    "retrieval": 0,
    "productive": 0,
    "quality": 0,
    "focus": 0
  },
  "key_findings": ["..."],
  "risk_flags": ["..."],
  "recommendations": [
    {
      "title": "...",
      "impact": "high|med|low",
      "effort": "high|med|low",
      "steps": ["..."]
    }
  ]
}

## Evidence discipline
- Every numeric score must cite an evidence path.
- Snippets must avoid secrets; report only presence + path for tokens/keys.
