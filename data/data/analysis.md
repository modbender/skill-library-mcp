# Analysis & Statistics

## Exploratory Data Analysis (EDA)

### First Look Checklist
```
□ Shape (rows × columns)
□ Column types and names
□ Missing values count and pattern
□ Numeric summary (mean, median, std, min, max, quartiles)
□ Categorical summary (unique values, top frequencies)
□ Date ranges (min, max, gaps)
□ Obvious outliers or anomalies
```

### Distribution Analysis
- **Histograms** for continuous variables — check for skew, multimodality
- **Value counts** for categorical — check for imbalance
- **Box plots** for outlier detection — IQR method
- **Time series plots** for temporal data — trends, seasonality

### Correlation Analysis
- Pearson for linear relationships (continuous)
- Spearman for monotonic relationships (ordinal)
- Point-biserial for continuous vs binary
- Chi-square for categorical vs categorical

**Trap:** Correlation ≠ causation. Always note this when reporting.

## Statistical Tests

### Choosing the Right Test

| Question | Data Types | Test |
|----------|------------|------|
| Means differ? (2 groups) | Continuous, normal | t-test |
| Means differ? (2 groups) | Continuous, non-normal | Mann-Whitney U |
| Means differ? (3+ groups) | Continuous, normal | ANOVA |
| Means differ? (3+ groups) | Continuous, non-normal | Kruskal-Wallis |
| Proportions differ? | Categorical | Chi-square |
| Variables related? | Both continuous | Correlation |
| Before/after change? | Paired continuous | Paired t-test |

### Assumption Checking
- **Normality:** Shapiro-Wilk test, Q-Q plot
- **Homogeneity of variance:** Levene's test
- **Independence:** study design, not testable from data
- **Sample size:** rule of thumb n ≥ 30 for parametric

### Interpreting Results
```
Report:
- Test statistic value
- p-value
- Effect size (Cohen's d, r², odds ratio)
- Confidence interval
- Practical significance, not just statistical
```

## A/B Test Analysis

### Before Running
- Define success metric clearly
- Calculate required sample size (power analysis)
- Set significance level (typically α = 0.05)
- Determine minimum detectable effect

### During Analysis
```
1. Check randomization — groups should be balanced on key dimensions
2. Check sample ratio — expected 50/50? Verify
3. Calculate metric for each group
4. Run appropriate statistical test
5. Calculate confidence interval
6. Check for novelty effect if time-based
```

### Common Pitfalls
- **Peeking** — checking significance repeatedly inflates false positive rate
- **Post-hoc segmentation** — finding subgroups that "worked" is fishing
- **Ignoring effect size** — statistically significant ≠ meaningful
- **Short run time** — day-of-week effects, novelty wear-off

## Pattern Discovery

### Segmentation
- K-means for numeric features
- Hierarchical for interpretable clusters
- DBSCAN for arbitrary shapes, outlier detection
- RFM (Recency, Frequency, Monetary) for customer data

### Anomaly Detection
- Z-score: |z| > 3 typically flagged
- IQR: below Q1 - 1.5×IQR or above Q3 + 1.5×IQR
- Isolation Forest: for multivariate
- Time series: seasonal decomposition + residual analysis

### Trend Analysis
- Moving averages for smoothing
- Year-over-year, month-over-month comparisons
- Decomposition: trend + seasonal + residual
- Growth rate calculation: (current - previous) / previous
