# Earned Value Dashboard

## Project: {{PROJECT_NAME}}
**Report Date:** {{DATE}}
**Project Manager:** {{PM_NAME}}

---

## Executive Summary

| Overall Health | Schedule Health | Cost Health |
|----------------|-----------------|-------------|
| {{STATUS}} | {{STATUS}} | {{STATUS}} |

---

## Key Metrics

### Budget Status
| Metric | Value | Status |
|--------|-------|--------|
| **Total Budget (BAC)** | ${{BAC}} | - |
| **Estimate at Completion (EAC)** | ${{EAC}} | {{STATUS}} |
| **Variance at Completion (VAC)** | ${{VAC}} | {{STATUS}} |
| **Estimate to Complete (ETC)** | ${{ETC}} | - |

### Performance Indices
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| **Cost Performance Index (CPI)** | {{CPI}} | >0.95 | {{STATUS}} |
| **Schedule Performance Index (SPI)** | {{SPI}} | >0.90 | {{STATUS}} |
| **To Complete Performance Index (TCPI)** | {{TCPI}} | >1.0 | {{STATUS}} |

### Variances
| Metric | Formula | Value | Interpretation |
|--------|---------|-------|----------------|
| **Cost Variance (CV)** | EV - AC | ${{CV}} | {{INTERPRETATION}} |
| **Schedule Variance (SV)** | EV - PV | ${{SV}} | {{INTERPRETATION}} |

---

## Trend Analysis

### S-Curve
```
Budget
  ↑
  |        _____
BAC|      /      \
  |    /         \________
  |___/                    \
  |_____________________________\____ Time
    |      |      |      |      |
    Start   PV     Now    EAC   BAC
```

### Weekly/Bi-weekly Trends

| Period | PV | EV | AC | CPI | SPI | Status |
|--------|----|----|----|-----|-----|--------|
| Week 1 | | | | | | |
| Week 2 | | | | | | |
| Week 3 | | | | | | |
| ... | | | | | | |

---

## Alerts & Warnings

### 🔴 Critical Issues
- {{ISSUE_1}}

### 🟡 Warnings
- {{WARNING_1}}

### ✅ Positive Trends
- {{POSITIVE_1}}

---

## Forecast Scenarios

| Scenario | Planned | CPI-Based | AC-Based |
|----------|---------|-----------|----------|
| **EAC** | {{BAC}} | {{EAC_CPI}} | {{EAC_AC}} |
| **Days Remaining** | {{PLANNED}} | {{FORECAST_CPI}} | {{FORECAST_AC}} |
| **Completion** | {{DATE}} | {{DATE}} | {{DATE}} |

---

## Action Plan

### Immediate Actions (This Week)
- [ ] {{ACTION_1}} - Owner: {{OWNER}} Due: {{DATE}}

### Short-Term Actions (Next 2 Weeks)
- [ ] {{ACTION_1}} - Owner: {{OWNER}} Due: {{DATE}}

### Long-Term Actions
- [ ] {{ACTION_1}} - Owner: {{OWNER}} Due: {{DATE}}

---

## Data Sources

| Document | Date | Owner |
|----------|------|-------|
| Project Plan | {{DATE}} | {{NAME}} |
| Timesheets | {{DATE}} | {{NAME}} |
| Progress Reports | {{DATE}} | {{NAME}} |

---

**Report Compiled by:** {{NAME}}
**Next EVM Review:** {{DATE}}
**Distributed to:** {{STAKEHOLDERS}}
