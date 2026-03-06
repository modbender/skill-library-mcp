# Risk Disclosure — Swaps Intelligence (Skill + ChatGPT Mini App + iOS App)

This skill exposes blockchain analytics and risk scoring. It carries domain-specific risks:

## 1) False Positive / False Negative Risk
Risk signals can be wrong or incomplete due to chain obfuscation, bridge complexity, timing gaps, or external data quality.

## 2) Attribution Risk
Labels may indicate probabilistic associations, not judicially proven attribution.

## 3) Operational Risk
If users act solely on one signal (freeze request, report, escalation), they may cause delay, friction, or legal exposure.

## 4) Legal/Regulatory Framing Risk
Misrepresenting outputs as definitive legal or compliance conclusions increases liability risk.

## 5) Abuse Risk
Open API access can be misused for targeting, harassment, or doxxing if guardrails are weak.

---

## Required Mitigations (must keep)
- Show disclaimer in user-facing outputs
- Use confidence/risk language ("signal", "indicator", "heuristic")
- Keep logs minimal; avoid storing unnecessary personal data
- Enforce key-based auth, rate limits, and abuse detection
- Provide challenge/correction path for disputed labels

## Recommended Response Framing
- "High risk signal detected" ✅
- "Known scammer confirmed" ❌

- "Potential sanctions exposure" ✅
- "Criminal address" ❌
