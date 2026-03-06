# Problem Diagnosis

## Diagnostic Flow

When user reports a problem:

1. **Identify the symptom** (yellow leaves, spots, wilting, pests visible)
2. **Check plant history** → `plants/{name}.md` for past issues
3. **Check zone conditions** → `zones/{zone}.md` for environmental factors
4. **Cross-reference patterns** → same issue in multiple plants?
5. **Suggest likely causes** ranked by probability
6. **Recommend treatment** with specific steps
7. **Log the diagnosis** in plant's health history

## Common Symptoms → Causes

### Yellow Leaves

| Pattern | Likely Cause | Check |
|---------|--------------|-------|
| Lower leaves first | Nitrogen deficiency | When last fertilized? |
| Between veins (interveinal) | Iron/magnesium deficiency | Soil pH? |
| All over, plus wilting | Overwatering | Soil moisture? Drainage? |
| Spots with yellow halo | Fungal infection | Recent rain/humidity? |
| New growth yellow | pH lock-out | Soil test needed |

### Wilting

| Pattern | Likely Cause | Check |
|---------|--------------|-------|
| Midday only, recovers evening | Heat stress | Normal for hot days |
| Constant, soil is wet | Root rot | Drainage, reduce water |
| Constant, soil is dry | Underwatering | Increase frequency |
| Sudden, one side of plant | Bacterial wilt | Inspect stem, may be fatal |
| Progressive from bottom | Fusarium/Verticillium | Check rotation history |

### Spots & Discoloration

| Pattern | Likely Cause | Treatment |
|---------|--------------|-----------|
| Brown spots, concentric rings | Early blight | Remove affected leaves, fungicide |
| Black spots on roses | Black spot fungus | Improve air circulation, fungicide |
| White powder on leaves | Powdery mildew | Baking soda spray, improve airflow |
| Rust-colored spots underside | Rust fungus | Remove affected parts, avoid wetting leaves |
| Mosaic pattern, distortion | Virus | Remove plant, control aphids |

### Pest Identification

| Signs | Pest | Action |
|-------|------|--------|
| Sticky residue, tiny insects | Aphids | Spray off, neem, ladybugs |
| Silver trails, holes | Slugs/snails | Beer traps, diatomaceous earth |
| Webbing under leaves | Spider mites | Increase humidity, neem |
| Holes in leaves, green caterpillars | Caterpillars | Handpick, Bt spray |
| Wilting despite water, grubs in soil | Root pests | Beneficial nematodes |

## Questions to Ask

When diagnosing, gather:

1. **Which plant(s)?** → Load plant history
2. **When did it start?** → Correlate with weather/activity
3. **Affected area?** → All leaves, new growth, old growth, one side?
4. **Recent changes?** → New fertilizer, moved, weather event?
5. **Photo?** → If available, visual diagnosis

## Logging Diagnoses

Update plant's health log:

```markdown
## Health Log
| Date | Issue | Treatment | Outcome |
|------|-------|-----------|---------|
| 2026-06-20 | Yellow lower leaves | Applied nitrogen fertilizer | Improved in 1 week |
| 2026-07-05 | Aphids | Neem spray x3 days | Cleared |
| 2026-07-20 | Blossom end rot | Consistent watering + calcium | No new affected fruit |
```

## Pattern Recognition

After logging issues:

- Same plant, recurring problem → Note variety weakness
- Same zone, multiple plants → Environmental issue
- Same pest, every year → Add to spring prevention checklist
- Same timing → Correlate with climate events

## Prevention Reminders

Based on history, suggest preventive actions:

"Last year aphids appeared in June. Consider:
- Inspect new growth weekly starting late May
- Plant nasturtiums as trap crop
- Encourage ladybugs"
