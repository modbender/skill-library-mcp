# Premortem Effectiveness: Expected Impact Areas

## Why Measurement Matters

Premortem is a reasoning pattern, not a tool. Its impact is measured by the
ABSENCE of failures rather than the presence of features. These are the
dimensions where premortem-equipped agents are expected to outperform baseline.

## Impact Dimensions

### 1. First-Attempt Success Rate

Without premortem: Agents often need 2-3 iterations to get code right.
With premortem: The failure-prediction pass catches issues before the first attempt.

**Expected improvement**: Fewer revision cycles, less wasted context window.

### 2. Intent Alignment Score

Without premortem: Agents drift from user intent over long conversations.
With premortem: The "Snapshot Intent" phase creates recurring anchor points.

**Expected improvement**: Responses stay closer to what the user actually asked.

### 3. Hallucination Frequency

Without premortem: Agents confidently state incorrect information.
With premortem: The "Can I point to where I learned this?" check flags uncertain claims.

**Expected improvement**: Fewer hallucinated facts, better confidence calibration.

### 4. Security Vulnerability Introduction

Without premortem: Agents sometimes generate code with injection vulnerabilities.
With premortem: The security lens catches common vulnerability patterns.

**Expected improvement**: Fewer OWASP Top 10 vulnerabilities in generated code.

### 5. Blast Radius Awareness

Without premortem: Agents sometimes take actions with unintended side effects.
With premortem: The side-effects lens maps consequences before action.

**Expected improvement**: Fewer unintended changes, better change containment.

## Cost Analysis

| Resource | Cost |
|----------|------|
| API calls | 0 |
| External services | 0 |
| Dependencies | 0 |
| Storage | 0 |
| Compute | Negligible (internal reasoning only) |
| Context window | ~2-5% per premortem pass |
| Latency | ~0.5-2s per premortem pass |

**Total cost: Effectively zero.** The only "cost" is a small amount of context
window and latency, both negligible compared to the quality improvement gained.

## When Premortem Saves the Most

The highest-value premortem scenarios (where failure prevention saves the most
time and effort):

1. **Irreversible actions** — Deleting data, force-pushing, deploying to production
2. **Complex refactors** — Multi-file changes where one mistake cascades
3. **Ambiguous requirements** — When the user hasn't fully specified what they want
4. **High-confidence hallucination zones** — Topics where the agent "feels" confident
   but evidence is thin
5. **Long conversations** — Where context decay and intent drift are greatest
