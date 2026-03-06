# Carrier Selection - Shipping Operations

## Service Selection Matrix

| Priority | Best fit | What to optimize |
|----------|----------|------------------|
| Lowest cost | Economy ground | Total landed cost and surcharge exposure |
| Fast delivery | Express air | On-time performance and recovery speed |
| Fragile/high value | Premium tracked service | Scan fidelity, insurance, claim quality |
| Cross-border | Carrier with customs support | Documentation quality and clearance speed |

## Minimum Inputs Before Quoting

- Origin and destination postal codes
- Package dimensions, weight, and quantity
- Delivery deadline and weekend requirement
- Declared value and insurance intent
- Signature requirement and remote-area risk

No final recommendation without these inputs.

## Landed Cost Formula

Use this formula for each candidate option:

```text
landed_cost = base_rate
            + fuel_surcharge
            + residential_or_remote_fees
            + additional_handling
            + signature_or_insurance
            + brokerage_duties_taxes
            + packaging_cost
```

Always compare options at equal service level and equal delivery promise.

## Dimensional Weight Guardrail

Calculate and compare:

```text
dim_weight = (length * width * height) / carrier_divisor
billable_weight = max(actual_weight, dim_weight)
```

If dim weight dominates, re-evaluate packaging before buying label.

## Recommendation Template

When presenting options, include:
- Option name and expected delivery window
- Total landed cost breakdown
- Top risks (delay, surcharge, claim friction)
- Why this option wins for the stated priority

Keep recommendation short and decision-ready.

## Red Flags

- Rate quote missing surcharges
- Delivery promise with no historical lane evidence
- Insurance excluded for high-value shipments
- Label purchase before package dimensions are confirmed
