# Item Calibration Guide

Calibration estimates the IRT parameters (a, b, c) for each question in your item bank.

## Prerequisites

**Minimum sample size per item:**
- 3PL model: 1000+ responses
- 2PL model: 500+ responses  
- 1PL/Rasch: 200+ responses

**Data required:**
- Item responses (correct/incorrect)
- Person identifiers (can be anonymous)
- No missing data patterns that are systematically related to ability

## Calibration Process

### 1. Collect Pilot Data

**Field test design:**
- Random assignment: Each student gets a random subset of items
- Spiraling: Rotate item sets across students
- Embedded pilot: Mix new items into operational tests (discard from scoring)

**Target:** Every item answered by ≥ minimum sample size

### 2. Estimate Parameters

**Software options:**
- **R:** `mirt` package (flexible, well-documented)
- **Python:** `mirt` (port), `girth` (fast), `pymc` (Bayesian)
- **Standalone:** BILOG-MG, MULTILOG, flexMIRT (commercial)

**Basic R example (2PL):**
```r
library(mirt)

# data: matrix where rows=students, cols=items, values=0/1
model <- mirt(data, model=1, itemtype='2PL')

# Extract parameters
params <- coef(model, simplify=TRUE)$items
# Columns: a (discrimination), b (difficulty), g (guessing), u (upper asymptote)
```

**For 3PL:** Change `itemtype='3PL'`. Warning: 3PL needs large samples or priors.

### 3. Check Model Fit

**Item-level diagnostics:**

**a. Item fit statistics**
- S-χ² (Orlando & Thissen): p > 0.01 = acceptable
- RMSEA (item): < 0.05 = good fit
- Run: `itemfit(model, method='S_X2')`

**b. Local independence**
- Check residual correlations: should be near zero
- Run: `residuals(model, type='LD')`

**c. Parameter flags**
- a < 0.5 → Low discrimination, consider removal
- a > 2.5 → May be measuring different construct
- b < -3 or b > 3 → Outside measurable range
- c > 0.35 → Guessing parameter too high (check item quality)

**Test-level diagnostics:**

**a. Test information curve**
- Should peak near target ability range
- Flat regions = poor measurement

**b. Marginal reliability**
- Similar to Cronbach's α but for IRT
- Target: > 0.80 for low-stakes, > 0.90 for high-stakes

### 4. Handle Problem Items

**If item doesn't fit:**

1. **Review content:** Is the question ambiguous? Multiple interpretations?
2. **Check key:** Is the correct answer actually correct?
3. **Inspect distractors:** Are wrong answers too obvious or confusing?
4. **Revise or remove:** Fix the item and recalibrate, or drop it

**If discrimination is too low (a < 0.5):**
- Often means item is poorly written
- May be testing memorization, not understanding
- Consider removal

**If discrimination is too high (a > 2.5):**
- May be "giveaway" item or testing different skill
- Check content alignment

### 5. Scale Linking (Optional)

If you're adding new items to an existing bank, you need to link scales:

**Concurrent calibration:** Calibrate old + new items together (preferred when feasible)

**Separate calibration + linking:**
1. Calibrate new items with separate sample
2. Use common items (anchor items) to link scales
3. Transform new item parameters to match old scale

**Linking methods:**
- Mean-sigma (simplest)
- Stocking-Lord (more robust)
- Haebara (optimal for 3PL)

**R example:**
```r
library(plink)

# old_params, new_params: data frames with a, b, c columns
# common_items: indices of anchor items

link <- plink(old_params[common_items,], new_params[common_items,], 
              method='Haebara')
              
# Transform new parameters to old scale
new_params_linked <- rescale(new_params, link$A, link$B)
```

## Classical Test Theory (CTT) Pre-Check

Before IRT calibration, run CTT diagnostics (fast and informative):

**Item difficulty (p-value):**
- p = proportion correct
- Target: 0.3 to 0.7 (for discrimination)
- p < 0.2 or p > 0.9 → May not work well in IRT

**Point-biserial correlation:**
- Correlation between item score and total score
- Target: > 0.20
- Negative values → Item is broken (check key)

**R example:**
```r
# data: 0/1 matrix
difficulty <- colMeans(data, na.rm=TRUE)
total_scores <- rowSums(data, na.rm=TRUE)

pb_corr <- sapply(1:ncol(data), function(i) {
  cor(data[,i], total_scores, use='complete.obs')
})
```

Flag items with:
- p < 0.10 or p > 0.95
- Point-biserial < 0.15

These are unlikely to calibrate well.

## Quality Checklist

Before finalizing calibration:

- [ ] All items have ≥ minimum sample size
- [ ] No negative discriminations (a > 0)
- [ ] Item fit statistics acceptable (S-χ² p > 0.01)
- [ ] Residual correlations < 0.20
- [ ] Parameters within expected ranges
- [ ] Test information curve covers target ability range
- [ ] Marginal reliability ≥ target threshold

## When to Recalibrate

- **Never:** Small changes in item wording, formatting
- **Consider:** Change in target population (e.g., switching grades)
- **Always:** Material content changes, correct answer changes, or suspect parameter drift (item used 2+ years)

**Drift detection:** If you have ongoing data, check if recent item performance differs from calibration sample. Flag items with p-value change > 0.10.

## Troubleshooting

**Problem:** 3PL won't converge  
**Solution:** Try 2PL first, or use Bayesian priors on c parameter

**Problem:** Discrimination estimates are all similar  
**Solution:** May indicate 1PL (Rasch) is more appropriate, or lack of variability in item quality

**Problem:** Some items have b > 3 or b < -3  
**Solution:** Items are outside measurable range for this population. Use different sample or remove items.

**Problem:** Large standard errors on parameters  
**Solution:** Increase sample size or use Bayesian estimation with priors
