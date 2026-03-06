# Data Schemas and Health/Safety Thresholds

## Contractions JSON schema

- **Root**: array of objects.
- **Each object**:
  - `id`: string (UUID).
  - `startTime`: string, ISO 8601 (e.g. `2026-01-30T19:09:20Z`).
  - `endTime`: string, ISO 8601.

**Derived**:
- **Duration** = `endTime - startTime` (seconds or minutes).
- **Interval** = time from previous contraction's `endTime` to this contraction's `startTime` (minutes). First contraction has no interval.

Sort by `startTime` ascending for chronological analysis.

---

## Baby logs JSON schema

- **Root**: object.
  - `birthday`: string, ISO 8601 (baby's date of birth).
  - `babyLog`: array of log entries.
- **Each entry**:
  - `id`: string (UUID).
  - `timestamp`: string, ISO 8601.
  - `type`: `"feeding"`, `"diaper"`, or `"breastFeeding"`.
  - If `type === "feeding"`: `feedingDetails.volumeML` (number, mL).
  - If `type === "diaper"`: `diaperDetails.hasPee` (boolean), `diaperDetails.hasPoo` (boolean).
  - If `type === "breastFeeding"`: `breastFeedingDetails.durationSeconds` (number).

**Derived**:
- **Baby age** = (latest log date or "now") − `birthday` (days or weeks).
- **Last 24 h** = entries with `timestamp` in the 24 hours before the latest entry (or current time).

---

## Mum – Contraction safety thresholds

- **5-1-1 rule (often "go to hospital")**: Contractions **5** minutes apart (or less), lasting **1** minute (or more), for **1** hour or more. → **Seek care / go to hospital**.
- **Regular and progressing**: Intervals shortening and/or duration lengthening over time → **Monitor closely**; consider calling midwife/OB.
- **Irregular, infrequent, or short**: e.g. >5 min apart, <45 s duration, not regular → often **Braxton Hicks** or early labour; **mum likely safe**, continue timing.
- **Very frequent** (e.g. <2 min apart) and strong → **Seek care**.
- **Any concern** (bleeding, waters broken, reduced movement, pain, distress) → **Seek care** regardless of contraction pattern.

**Verdict wording**:
- **Mum safe**: Pattern not suggestive of active labour requiring immediate care; continue monitoring.
- **Monitor**: Pattern could be early/active labour; time contractions and consider calling provider.
- **Seek care**: 5-1-1 or other red flags; go to hospital or call midwife/OB.

---

## Baby – Feeding and diaper thresholds (newborn / early weeks)

Approximate guidelines (adjust for paediatrician advice and individual baby):

### Feeding (bottle / expressed milk, volume in mL)

- **Frequency**: ~8–12 feeds per 24 h for newborns; can be every 2–3 h.
- **Volume (rough)**:
  - Day 1: ~5–10 mL per feed.
  - First week: increase to ~30–60 mL per feed.
  - By ~1 month: ~80–120 mL per feed, ~8+ feeds per day.
- **Red flags**: Very low total volume in 24 h, very long gaps (>4 h) without feed, or refusal to feed → **Concern / discuss with paediatrician**.

### Breastfeeding (sessions, duration in seconds)

- **Sessions**: Count entries with `type === "breastFeeding"`; report count and total duration (e.g. total minutes = sum of `durationSeconds` / 60) over last 24 h.
- **Typical**: Newborns often feed 8–12+ times per 24 h; session length varies (e.g. 10–40+ minutes). Combined bottle + breastfeeding count toward overall feed frequency.
- **Red flags**: Very few sessions in 24 h, or very short total duration with signs of poor transfer → **Monitor / discuss with lactation support or paediatrician**.

### Diapers

- **Wet (hasPee)**: At least **6+ wet diapers per 24 h** once milk is established (by ~day 5). Fewer may suggest low intake or dehydration.
- **Dirty (hasPoo)**: Variable; several per day is common in early weeks; some babies less often. No poo for many days in a newborn can be a concern.
- **Red flags**: Few wet diapers, no poo for extended time, or very dry nappies → **Concern / discuss with paediatrician**.

**Verdict wording**:
- **Baby healthy**: Feeds and wet/dirty diaper counts in expected range for age; no red flags.
- **Monitor**: Slightly low/high feeds or diapers; suggest tracking and next feed/diaper check.
- **Concern**: Low intake, few wet diapers, or other red flags; recommend contacting paediatrician or health visitor.

---

## Caveat

These thresholds are for **supporting a structured summary**, not for medical diagnosis or treatment. Always advise: when in doubt, contact a midwife, OB, or paediatrician.
