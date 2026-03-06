# Adaptive Testing Concepts

> Background on Item Response Theory (IRT) and Computerized Adaptive Testing (CAT) for AI agents using the AdaptiveTest API.

---

## Item Response Theory (IRT)

IRT is a psychometric framework that models the probability of a correct response as a function of the person's ability and the item's characteristics.

### Models

**2PL (Two-Parameter Logistic):**
```
P(correct | theta, a, b) = 1 / (1 + exp(-a * (theta - b)))
```
- `theta` -- person ability (typically -3 to +3)
- `a` -- discrimination (how well the item differentiates ability levels, typically 0.5 to 2.5)
- `b` -- difficulty (the ability level at which P(correct) = 0.5, typically -3 to +3)

**3PL (Three-Parameter Logistic):**
```
P(correct | theta, a, b, c) = c + (1 - c) / (1 + exp(-a * (theta - b)))
```
- `c` -- guessing/pseudo-chance parameter (lower asymptote, typically 0.1 to 0.35 for 4-option MC)

### Key Concepts

**Ability (theta):** A latent trait score on a standardized scale. Mean = 0, SD = 1. A theta of 1.5 means the person is 1.5 standard deviations above average.

**Item Information:** How much an item contributes to measurement precision at a given ability level. Items are most informative when their difficulty matches the examinee's ability.

**Standard Error (SE):** Precision of the ability estimate. Lower SE = more precise. SE decreases as more items are administered. Typical stopping threshold: SE < 0.3.

**Test Information Function (TIF):** Sum of all item information functions. Shows where on the ability scale the test measures most precisely.

---

## Computerized Adaptive Testing (CAT)

CAT dynamically selects items based on the examinee's estimated ability, maximizing measurement precision with fewer items.

### How CAT Works

1. **Initialize:** Start with prior ability estimate (theta = 0, SE = 1.0)
2. **Select item:** Choose the item with maximum information at current theta estimate
3. **Administer item:** Present the selected item to the examinee
4. **Score response:** Record correct/incorrect
5. **Update estimate:** Recalculate theta and SE using all responses so far (EAP or MLE)
6. **Check stopping rule:** If SE < threshold OR max items reached, stop. Otherwise, go to step 2.

### Stopping Rules

AdaptiveTest supports these stopping conditions (whichever triggers first):
- **SE threshold:** SE < 0.3 (configurable per test)
- **Maximum items:** Reached `max_items` count
- **Minimum items:** At least 5 items administered before SE check

### Advantages Over Fixed-Form Tests

- **40-60% fewer items** for equivalent measurement precision
- **Precise at all ability levels** (not just the middle of the distribution)
- **Each student gets a unique test** tailored to their level
- **Faster:** Students finish sooner because irrelevant items are skipped
- **More engaging:** Items are appropriately challenging, reducing frustration and boredom

### Item Pool Requirements

For effective CAT:
- Minimum 3x the max session length in items (e.g., 60 items for 20-item sessions)
- Items should span the full difficulty range (-3 to +3)
- High discrimination items (a > 1.0) are preferred
- Items need calibrated IRT parameters (see `references/calibration.md`)

---

## Mastery Levels

AdaptiveTest maps theta to mastery levels:

| Theta Range | Mastery Level | Description |
|-------------|---------------|-------------|
| theta < -1.0 | Below Basic | Significant gaps in understanding |
| -1.0 <= theta < 0.0 | Basic | Partial understanding, needs support |
| 0.0 <= theta < 1.0 | Proficient | Meets grade-level expectations |
| theta >= 1.0 | Advanced | Exceeds expectations |

---

## Practical Guidance for AI Agents

### When to Use Adaptive Testing
- Placement tests (where is this student?)
- Diagnostic assessments (what does this student know?)
- Progress monitoring (how is this student growing?)
- Any scenario where measurement precision matters more than content coverage

### When NOT to Use Adaptive Testing
- Content mastery checklists (student must see all items)
- Practice quizzes (where the goal is exposure, not measurement)
- Tests with very few items (< 10 items, CAT adds little value)

### Setting Up a Good Adaptive Test
1. Create a large, well-calibrated item pool (see calibration guide)
2. Enable CAT: `cat_enabled: true`
3. Set appropriate max items (15-30 is typical)
4. Use 3PL model for multiple-choice items (accounts for guessing)
5. Monitor item usage statistics to prevent overexposure
