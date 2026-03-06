---
name: Statistics
description: Build statistical intuition from basic probability to advanced inference.
metadata: {"clawdbot":{"emoji":"📊","os":["linux","darwin","win32"]}}
---

## Detect Level, Adapt Everything
- Context reveals level: notation familiarity, software mentioned, problem complexity
- When unclear, start with concrete examples and adjust based on response
- Never condescend to experts or overwhelm beginners

## For Beginners: Intuition Before Formulas
- Probability through physical objects — dice, coins, cards, colored balls in bags
- Averages as balance points — "If everyone shared equally, each would get..."
- Variation matters as much as center — two classes with same average, very different spreads
- Graphs before numbers — show the shape, then quantify it
- Sampling as tasting soup — one spoonful tells you about the pot if well stirred
- Correlation isn't causation — ice cream sales and drowning both rise in summer
- Connect to their decisions — weather forecasts, medical tests, sports statistics

## For Students: Frameworks and Assumptions
- Name the test AND its assumptions — normality, independence, equal variance
- Effect size alongside p-value — statistical significance ≠ practical importance
- Confidence intervals tell richer stories than hypothesis tests alone
- Distinguish population parameters from sample statistics — Greek vs Roman letters matter
- Simulation builds intuition — bootstrap, permutation tests show what formulas hide
- Regression diagnostics before interpretation — residual plots catch violations
- Bayesian vs frequentist — acknowledge the philosophical divide, explain context for each

## For Researchers: Rigor and Honesty
- Pre-registration prevents p-hacking — specify analysis before seeing data
- Power analysis before collecting — underpowered studies waste resources
- Multiple comparisons require adjustment — Bonferroni, FDR, or justify why not
- Report effect sizes and confidence intervals — not just p-values
- Missing data mechanisms matter — MCAR, MAR, MNAR require different treatments
- Causal inference needs design — DAGs, potential outcomes, state assumptions explicitly
- Reproducibility means code and data — "available upon request" is not reproducible

## For Teachers: Common Misconceptions
- p-value is NOT probability hypothesis is true — it's probability of data given null
- Failing to reject ≠ accepting null — absence of evidence isn't evidence of absence
- Large samples don't fix bias — garbage in, garbage out regardless of n
- Standard deviation vs standard error — population spread vs sampling precision
- Correlation coefficient hides nonlinearity — always plot first
- Use real messy data — textbook examples with clean answers mislead
- Teach skepticism — "How was this measured? Who was sampled? What's missing?"

## Always
- Visualize data before computing anything
- State assumptions explicitly — every test has them
- Distinguish exploratory from confirmatory — same data can't do both
