# Retention Optimization

## Target Metrics

| Metric | Target | Red Flag |
|--------|--------|----------|
| Retention rate | 85-90% | <80% or >95% |
| Ease factor (avg) | 250% | <200% ("ease hell") |
| Leeches | <2% of cards | >5% |
| Daily reviews | Sustainable | >300/day burnout risk |

**<80% retention:** Cards are too hard or poorly written
**>95% retention:** Intervals too short, wasting time reviewing easy cards

## Ease Hell

**What it is:** Cards with ease factors that dropped so low (130-180%) they're reviewed too frequently, creating a death spiral.

**How it happens:**
1. Fail a card → ease drops 20%
2. Review again quickly → still hard → fail again
3. Ease drops more → even shorter intervals
4. Card becomes a daily leech consuming review time

**Detection:**
- Many cards with ease <200%
- Reviews dominated by same cards
- Retention okay but review count exploding

**Fixes:**
1. Manual ease reset: `set ease to 250%` for affected cards
2. Use FSRS (auto-adjusts, no ease factor)
3. Rewrite the card (bad card, not bad memory)

## Leech Management

**Default threshold:** 8 failures → suspended

**Leech causes:**
- Bad card wording (most common)
- Interference with similar cards
- Lack of context/cues
- Arbitrary fact with no mnemonic
- Card tests multiple things

**Fix process:**
1. Identify WHY you fail (wording? interference? forgetting?)
2. Rewrite with better cues or mnemonic
3. If truly arbitrary, add memorable hook
4. If interference, differentiate from similar cards
5. Reset repetition history after rewrite

## Settings Optimization

### New Cards per Day
- Start: 10-20/day
- Max sustainable: where reviews stay <150/day
- Reduce if reviews pile up >200/day

### Graduating Interval
Default 1 day → consider 3-4 days if retention is high

### Easy Bonus
Default 1.3 → increase to 1.5 if "easy" cards still show up too often

### Maximum Interval
Default 36500 (100 years) → reasonable to cap at 180-365 days for exam prep

### Interval Modifier
- Below 85% retention: decrease (reviews come faster)
- Above 92% retention: increase (reviews spread out)
- Formula: log(desired retention) / log(current retention)

## FSRS vs SM-2

**SM-2 (default):** Fixed algorithm, ease factor can spiral, no personalization
**FSRS:** ML-based, learns your patterns, no ease factor, generally better retention

**Should you switch?**
- If in ease hell → yes
- If happy with current → optional
- If <1000 reviews → not enough data for FSRS

**Migration:**
1. Backup first
2. Enable FSRS in deck options
3. Run "Optimize FSRS parameters" (needs review history)
4. Cards will reschedule based on new algorithm

## Review Backlog Recovery

When reviews pile up (vacation, burnout):

1. **Don't panic-review** — 500 reviews/day leads to more burnout
2. **Set daily limit** — 100-150 max, even if behind
3. **Bury excess** — Better to review some well than all poorly
4. **Reduce new cards to 0** — Until backlog clears
5. **Consider filtered deck** — Focus on most overdue or highest priority

## Stats Interpretation

**True retention:** Your actual recall rate. Look at "Answer Buttons" → (Good + Easy) / Total

**Intervals:** Check "Card Intervals" histogram. Spike at low intervals = possible ease hell.

**Review heatmap:** Consistent daily reviews > sporadic marathon sessions.

**Future due:** If this spikes, reduce new cards or you're building toward overwhelm.
