# Learnings

> Insights, corrections, and best practices. Promote recurring patterns to SOUL.md or AGENTS.md.

| Date | Category | Situation | Learning | Promoted? |
|------|----------|-----------|----------|-----------|
| | correction | | | |
| | knowledge_gap | | | |
| | best_practice | | | |

## VFM Protocol (Value-First Modification)
Before modifying SOUL.md, AGENTS.md, TOOLS.md, or cron configs, score the change:

| Dimension | Weight | Question |
|-----------|--------|----------|
| High Frequency | 3x | Used daily? |
| Failure Reduction | 3x | Turns failures into successes? |
| User Burden | 2x | Reduces human's effort? |
| Self Cost | 2x | Saves tokens/time for future sessions? |

Threshold: If weighted score < 50, don't do it.

### Anti-Drift Rules
- ❌ Don't add complexity to "look smart"
- ❌ Don't make unverifiable changes
- ❌ Stability > Explainability > Reusability > Novelty
