# BRS Policy - Official Standard

**Last Updated:** 2026-02-22  
**Status:** OFFICIAL & APPROVED ✅

## Policy

**All Aavegotchi tools MUST use TOTAL BRS (base + wearables modifiers)**

This is the gotchi's **true power level** with all equipped gear.

## Implementation

### gotchi-finder Skill

**JSON Output:**
- Primary field: `brs` = TOTAL BRS (modifiedRarityScore from contract)
- Reference field: `baseBrs` = Base BRS (baseRarityScore from contract)

**Console Display:**
```
⭐ Total BRS: 670 (Base: 562 + Wearables: +108)
```

### Gotchi Card Generator

**Uses `brs` field from gotchi-finder** → Shows TOTAL BRS on card

**Badge Display:**
```
Top-right: BRS 670 ⭐
```

**Rarity Tier:** Determined from TOTAL BRS
- GODLIKE: ≥600
- MYTHICAL: ≥550
- LEGENDARY: ≥525
- RARE: ≥500
- UNCOMMON: ≥475
- COMMON: <475

## Why Total BRS?

1. **Battle Strength** - Shows actual combat power
2. **Wearables Matter** - Reflects gear investment
3. **Rarity Tiers** - A gotchi can jump tiers with wearables
4. **Consistency** - Matches Baazaar listings & community tools

## Example

**SHAAMAAN (#22470):**
- Base BRS: 562 (MYTHICAL tier naturally)
- Wearables: +108 bonus
- **Total BRS: 670 (GODLIKE tier with gear!)** 🔥

## Contract Fields

From `getAavegotchi()`:
- `baseRarityScore` - Trait-based BRS (no wearables)
- `modifiedRarityScore` - **TOTAL BRS** (includes wearables) ← USE THIS

## Migration Notes

**Before:** Used `baseRarityScore`  
**After:** Use `modifiedRarityScore`

**Breaking Change:** ✅ Yes - BRS values increased for gotchis with wearables

**Impact:** Shows true power, some gotchis jump rarity tiers

---

**This is the approved standard for all AAI Aavegotchi tools.** 🎴✨
