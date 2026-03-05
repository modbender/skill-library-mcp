# Drift Detection and Monitoring

## Types of Drift

| Type | What Changes | Detection | Delay |
|------|--------------|-----------|-------|
| Data drift | Input distribution | PSI, KS-test | Immediate |
| Concept drift | Input→Output relationship | Accuracy drop | Needs labels |
| Prediction drift | Output distribution | Distribution stats | Immediate |
| Feature importance drift | Feature weights | SHAP/importance | Needs analysis |

## Alert Thresholds

**Tiered alerting:**
- Warning: 5% metric drop → Slack notification
- Critical: 15% drop → On-call page
- Emergency: 25%+ drop → Auto-rollback + incident

**Correlate with external events:**
- New deployment
- Data pipeline change
- Upstream service modification
- Seasonal patterns

## Observability Gaps

**What agents typically miss:**
- ❌ Only monitors latency/uptime, ignores model metrics
- ❌ No correlation between degradation and data pipeline changes
- ❌ Logs predictions but no samples for debugging
- ❌ Ignores fairness/bias monitoring in production

**What to monitor:**
- Prediction distribution (histogram over time)
- Feature value ranges
- Null/missing value rates
- Inference latency percentiles (p50, p95, p99)
- Model confidence distribution

## Retraining Triggers

**Not just "drift > X":**
- Consider retraining cost (compute, validation time)
- Data freshness requirements
- Business impact of current performance
- Dependencies: if model A retrains, does model B need to?

**Retraining requires:**
- Human validation before production deploy
- Rollback plan ready
- Shadow testing period
