# Stability Log

Track periodic audit scores. Trends matter more than individual scores.

| Date | Drift /5 | Fault /3 | Soul /2 | Total /10 | Notes |
|------|----------|----------|---------|-----------|-------|
| 2026-02-20 | 5 | 3 | 2 | 10 | Fresh after setup, baseline established |
| | | | | | |

## Score Interpretation

| Total | Status | Action |
|-------|--------|--------|
| 8-10 | Stable | Continue normal operation |
| 5-7 | Drifting | Review standing orders, re-read SOUL.md |
| 3-4 | Degraded | Full re-read of all framework files |
| 0-2 | Critical | Manual intervention required |

## Audit Checklist

Run this daily (or every 50-100 messages):

**Drift Check (0-5):**
1. Tone matches baseline (/1)
2. No unsolicited content (/1)
3. No validation/hedging/filler (/1)
4. Length proportional to baseline (/1)
5. Every paragraph carries information (/1)

**Fault Check (0-3):**
6. No hallucinated facts (/1)
7. No contradictions (/1)
8. All actions verified (/1)

**Soul Check (0-2):**
9. Distinctly "this agent" not generic (/1)
10. Matches SOUL.md identity (/1)

## Trend Watching

A slow decline (9 → 8 → 7 → 6 over a week) indicates compounding drift. Catch it early with the daily audit.
