# Statistical Tests for Fairness Auditing

## 1. Chi-Square Test for Randomness

Tests whether observed outcomes match expected distribution.

### For Dice (0-99):
- Bin results into 10 buckets (0-9, 10-19, ..., 90-99)
- Expected count per bucket: N/10
- χ² = Σ (observed - expected)² / expected
- df = 9 (10 bins - 1)
- p-value from chi-square distribution

```python
from scipy import stats
import numpy as np

def chi_square_test(results, bins=10):
    observed, _ = np.histogram(results, bins=bins, range=(0, 100))
    expected = np.full(bins, len(results) / bins)
    chi2, p_value = stats.chisquare(observed, expected)
    return {
        'chi2': chi2,
        'df': bins - 1,
        'p_value': p_value,
        'pass': p_value > 0.05
    }
```

### For Coinflip:
- Expected: 50% heads, 50% tails
- χ² = (heads - N/2)² / (N/2) + (tails - N/2)² / (N/2)
- df = 1

## 2. Kolmogorov-Smirnov Test

Tests if results follow uniform distribution.

```python
def ks_test(results):
    # Normalize to [0, 1]
    normalized = np.array(results) / 100.0
    stat, p_value = stats.kstest(normalized, 'uniform')
    return {
        'ks_statistic': stat,
        'p_value': p_value,
        'pass': p_value > 0.05
    }
```

## 3. Runs Test

Tests for serial independence (no patterns in win/loss sequences).

```python
def runs_test(outcomes):
    """outcomes: list of True/False (win/loss)"""
    n = len(outcomes)
    n1 = sum(outcomes)       # wins
    n0 = n - n1              # losses
    runs = 1 + sum(1 for i in range(1, n) if outcomes[i] != outcomes[i-1])
    
    # Expected runs
    expected = (2 * n0 * n1) / n + 1
    variance = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n * n * (n - 1))
    z = (runs - expected) / (variance ** 0.5)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    
    return {
        'runs': runs,
        'expected': expected,
        'z_score': z,
        'p_value': p_value,
        'pass': p_value > 0.05
    }
```

## 4. RTP Confidence Interval

Calculate confidence interval for observed RTP.

```python
def rtp_confidence_interval(payouts, wagers, confidence=0.95):
    rtp_values = np.array(payouts) / np.array(wagers)
    mean_rtp = np.mean(rtp_values)
    se = stats.sem(rtp_values)
    ci = stats.t.interval(confidence, len(rtp_values)-1, loc=mean_rtp, scale=se)
    return {
        'observed_rtp': mean_rtp,
        'ci_lower': ci[0],
        'ci_upper': ci[1],
        'confidence': confidence,
        'pass': ci[0] <= 0.99 <= ci[1]  # Expected RTP within CI
    }
```

## Interpretation Guide

| Test | PASS | FAIL |
|------|------|------|
| Chi-Square | p > 0.05 (results look random) | p < 0.05 (suspicious pattern) |
| KS Test | p > 0.05 (uniform distribution) | p < 0.05 (non-uniform) |
| Runs Test | p > 0.05 (no serial correlation) | p < 0.05 (patterns detected) |
| RTP CI | Expected RTP within interval | Expected RTP outside interval |

## Sample Sizes

- Minimum meaningful: 100 bets
- Good confidence: 500+ bets
- High confidence: 1000+ bets
- Publication quality: 10,000+ bets
