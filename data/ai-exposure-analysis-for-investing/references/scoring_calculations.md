# Scoring Calculations

Exact formulas for composite scores, sub-indices, classification matrix, and valuation overlay.

## Dimension Weights

| Dimension | Weight | Direction | Sub-Index |
|-----------|--------|-----------|-----------|
| 1. Labor Automation Vulnerability | 8% | Vulnerability | Vulnerability |
| 2. Revenue Model Disruption | 18% | Vulnerability | Vulnerability |
| 3. AI Adoption & Implementation ↑ | 10% | Capability | Adaptive Capacity |
| 4. Competitive Moat Durability | 16% | Vulnerability | Vulnerability |
| 5. Operational AI Leverage ↑ | 12% | Capability | Adaptive Capacity |
| 6. Regulatory & Ethical Risk | 3% | Vulnerability | Vulnerability |
| 7. Industry Transformation Velocity | 17% | Vulnerability | Vulnerability |
| 8. Data & Ecosystem Strength ↑ | 16% | Capability | Adaptive Capacity |

Vulnerability dimensions (1, 2, 4, 6, 7) total weight: 62%
Capability dimensions (3, 5, 8) total weight: 38%

## Step 1: AI Vulnerability Score

**Formula:** Weighted geometric mean of vulnerability dimensions.

```
Vulnerability = (D1^0.08 × D2^0.18 × D4^0.16 × D6^0.03 × D7^0.17) ^ (1 / 0.62)
```

The geometric mean penalizes extreme weakness — a collapsing moat (D4=5) cannot be offset by low labor costs (D1=1).

**Interpretation:**
- 1.0 – 2.5: Low Vulnerability
- 2.5 – 5.0: High Vulnerability

**Calculation example (from framework worked example):**
D1=4, D2=5, D4=4, D6=1, D7=5

```
= (4^0.08 × 5^0.18 × 4^0.16 × 1^0.03 × 5^0.17) ^ (1/0.62)
= (1.1180 × 1.3310 × 1.2457 × 1.0000 × 1.3077) ^ (1/0.62)
= (2.4254) ^ (1.6129)
≈ 3.95
```

Result: High Vulnerability (3.95)

## Step 2: AI Adaptive Capacity Score

**Formula:** Weighted average of capability dimensions, normalized to 1–5.

```
Adaptive Capacity = (D3 × 0.10 + D5 × 0.12 + D8 × 0.16) / 0.38
```

**Interpretation:**
- 1.0 – 3.5: Low Adaptive Capacity
- 3.5 – 5.0: High Adaptive Capacity

**Calculation example:**
D3=3.5, D5=2, D8=2.5

```
= (3.5 × 0.10 + 2 × 0.12 + 2.5 × 0.16) / 0.38
= (0.350 + 0.240 + 0.400) / 0.38
= 0.990 / 0.38
≈ 2.61
```

Result: Low-to-Moderate Adaptive Capacity (2.61)

## Step 3: 2×2 Matrix Classification

|  | Low Vulnerability (1–2.5) | High Vulnerability (2.5–5) |
|--|---------------------------|---------------------------|
| **High Adaptive Capacity (3.5–5)** | **AI FORTIFIED** — Low risk, high capability. Steady margin expansion from AI. | **AI TRANSFORMER** — High risk but aggressively adapting. Outperformance if execution succeeds. |
| **Low Adaptive Capacity (1–3.5)** | **AI BYSTANDER** — Low risk, low engagement. Stable but missing AI upside. | **AI ENDANGERED** — High risk, poor adaptation. Most vulnerable. Short candidates. |

**Classification boundaries:**
- Vulnerability threshold: 2.5
- Adaptive Capacity threshold: 3.5

**Borderline cases:** If either score is within 0.3 of a threshold, note it as "borderline" and explain which direction the company is trending (improving or deteriorating over the 4-year filing window).

## Step 4: Valuation Overlay

Compare the company's classification to its current market valuation relative to sector.

**Metrics to pull (Yahoo Finance or equivalent):**
- Company forward P/E ratio
- Company EV/Sales ratio
- Sector median forward P/E
- Sector median EV/Sales

**Valuation Signal Matrix:**

| Quadrant | Premium to Sector | In Line | Discount to Sector |
|----------|-------------------|---------|---------------------|
| AI Fortified | Fairly priced | Potential buy | Strong buy signal |
| AI Transformer | Priced for perfection | Fair if execution tracking | Mispricing opportunity |
| AI Bystander | Overvalued | Hold / neutral | Yield play only |
| AI Endangered | Short candidate | Avoid / reduce | Value trap until proven otherwise |

**How to determine premium/discount:**
- Forward P/E > 1.2× sector median = Premium
- Forward P/E 0.8–1.2× sector median = In Line
- Forward P/E < 0.8× sector median = Discount
- Apply same logic to EV/Sales. If the two metrics disagree, note the discrepancy.

## Step 5: Scenario Sensitivity

Assess how four emerging AI paradigms could shift the company's scores over 12–36 months:

| Paradigm | Description | Framework Impact |
|----------|-------------|-----------------|
| Agentic AI | AI autonomously completing multi-step workflows | Amplifies D2 for workflow-orchestration companies. Amplifies D7 for services. Increases D8 importance. |
| Physical AI / Robotics | AI-controlled robots in manufacturing, logistics, healthcare, agriculture | Reduces Tier 4 insulation. D1 scores for physical labor may rise from 1 to 2–3. Increases D5 for complex physical operations. |
| Energy Constraints | AI compute demand outstripping power supply | Advantages companies with owned power infrastructure. Could slow D7 in energy-constrained regions. Benefits Tier 4 energy/utility companies. |
| Open-Source AI Acceleration | Open-source models closing gap with proprietary | Erodes D8 for companies dependent on proprietary model access. Democratizes D3. Accelerates D7 everywhere. |

For each paradigm, note whether it would move any dimension score by ≥1 point and in which direction.

## Python Implementation

For automated calculation:

```python
import math

def calculate_vulnerability(d1, d2, d4, d6, d7):
    """Weighted geometric mean of vulnerability dimensions."""
    log_sum = (0.08 * math.log(d1) + 0.18 * math.log(d2) +
               0.16 * math.log(d4) + 0.03 * math.log(d6) +
               0.17 * math.log(d7))
    return math.exp(log_sum / 0.62)

def calculate_adaptive_capacity(d3, d5, d8):
    """Weighted average of capability dimensions."""
    return (d3 * 0.10 + d5 * 0.12 + d8 * 0.16) / 0.38

def classify(vulnerability, adaptive_capacity):
    """Classify into 2x2 matrix."""
    high_vuln = vulnerability > 2.5
    high_adapt = adaptive_capacity >= 3.5

    if high_adapt and not high_vuln:
        return "AI FORTIFIED"
    elif high_adapt and high_vuln:
        return "AI TRANSFORMER"
    elif not high_adapt and not high_vuln:
        return "AI BYSTANDER"
    else:
        return "AI ENDANGERED"

def valuation_signal(classification, pe_ratio, sector_pe):
    """Determine valuation signal."""
    if sector_pe == 0:
        return "Insufficient data"
    ratio = pe_ratio / sector_pe
    if ratio > 1.2:
        position = "Premium"
    elif ratio < 0.8:
        position = "Discount"
    else:
        position = "In Line"

    matrix = {
        ("AI FORTIFIED", "Premium"): "Fairly priced",
        ("AI FORTIFIED", "In Line"): "Potential buy",
        ("AI FORTIFIED", "Discount"): "Strong buy signal",
        ("AI TRANSFORMER", "Premium"): "Priced for perfection",
        ("AI TRANSFORMER", "In Line"): "Fair if execution tracking",
        ("AI TRANSFORMER", "Discount"): "Mispricing opportunity",
        ("AI BYSTANDER", "Premium"): "Overvalued",
        ("AI BYSTANDER", "In Line"): "Hold / neutral",
        ("AI BYSTANDER", "Discount"): "Yield play only",
        ("AI ENDANGERED", "Premium"): "Short candidate",
        ("AI ENDANGERED", "In Line"): "Avoid / reduce",
        ("AI ENDANGERED", "Discount"): "Value trap until proven otherwise",
    }
    return matrix.get((classification, position), "Unknown")

# Example usage:
vuln = calculate_vulnerability(d1=4, d2=5, d4=4, d6=1, d7=5)
adapt = calculate_adaptive_capacity(d3=3.5, d5=2, d8=2.5)
classification = classify(vuln, adapt)
print(f"Vulnerability: {vuln:.2f}")
print(f"Adaptive Capacity: {adapt:.2f}")
print(f"Classification: {classification}")
```
