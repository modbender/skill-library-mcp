---
name: wind-turbine-gearbox
description: Assesses wind turbine gearbox health from multi-sensor and inspection data. Classifies damage severity (1-5), identifies root cause, and recommends shutdown or monitoring actions.
version: 1.0.0
author: Sertug17
license: MIT
metadata:
  hermes:
    tags: [Energy, Maintenance, Wind-Turbine, Gearbox, Condition-Monitoring, Predictive-Maintenance, Vibration, Acoustics]
    related_skills: []
---

# Wind Turbine Gearbox Intelligence

Evaluates gearbox condition using five input parameters and produces a structured maintenance report.

## When to Use

Load this skill when the user wants to:
- Assess gearbox health from on-site inspection or sensor data
- Classify damage severity on a 1-5 scale
- Determine whether a turbine should be shut down or kept running under monitoring
- Generate a structured maintenance or escalation plan

## Quick Reference

| Input Parameter   | What to Collect                                            |
|-------------------|------------------------------------------------------------|
| Visual inspection | Surface cracks, pitting, spalling, discoloration, debris   |
| Oil iron (Fe ppm) | Iron particle concentration in gear oil (ppm)              |
| Temperature (C)   | Bearing/gear temperature, normalized to baseline           |
| Vibration         | RMS or peak-to-peak acceleration (g), frequency anomalies |
| Acoustic / Sound  | Noise type: grinding, knocking, whining, clicking          |

## Fault Thresholds (Reference)

| Parameter           | Normal        | Warning        | Critical       |
|---------------------|---------------|----------------|----------------|
| Oil Fe (ppm)        | < 100         | 100 - 300      | > 300          |
| Temp above baseline | < 5 C         | 5 - 15 C       | > 15 C         |
| Vibration RMS (g)   | < 0.5         | 0.5 - 1.5      | > 1.5          |
| Acoustic            | No anomaly    | Intermittent   | Continuous     |
| Visual              | Clean surface | Minor pitting  | Spalling/crack |

## Common Failure Modes

| Failure Mode     | Typical Indicators                                            |
|------------------|---------------------------------------------------------------|
| Micropitting     | High Fe ppm, slight vibration increase, no visible cracks    |
| Spalling         | High Fe ppm, elevated vibration, visible surface damage       |
| Fatigue crack    | Knocking sound, vibration spike at gear mesh frequency        |
| Bearing wear     | Whining noise, high temperature, broadband vibration increase |
| Oil contamination| Very high Fe ppm, discolored oil, possible foaming            |

## Procedure

1. Collect inputs across all five parameters. If any are unavailable, note as "not measured" and proceed.
2. Evaluate each parameter against the thresholds table. Flag Warning or Critical zones.
3. Cross-correlate symptoms:
   - Fe ppm + vibration increase → wear / spalling progression
   - Knocking sound + vibration spike → fatigue crack
   - Temperature + whining sound → bearing failure
   - Multiple Critical flags → Severity 5
4. Assign severity:
   - 1 Healthy: All parameters normal. No action required.
   - 2 Early wear: 1-2 parameters in warning zone. Increase monitoring frequency.
   - 3 Moderate damage: 2-3 parameters in warning/critical. Inspect within 2 weeks.
   - 4 Significant damage: Multiple critical flags. Plan shutdown within 48-72 hours.
   - 5 Critical: Imminent failure risk. Immediate shutdown required.
5. Determine root cause from the failure modes table.
6. Generate the output report using the format below.

## Output Format

=== GEARBOX HEALTH REPORT ===

ROOT CAUSE : [e.g., Progressive spalling on intermediate shaft gear]
SEVERITY   : [1-5] - [Healthy / Early Wear / Moderate / Significant / Critical]
SHUTDOWN   : [Yes / No / Conditional]

MONITORING STRATEGY:
  - [e.g., Repeat oil sample in 72 hours]
  - [e.g., Daily vibration trend monitoring for 1 week]

ESCALATION TRIGGERS:
  - [e.g., Fe ppm exceeds 400 - immediate shutdown]
  - [e.g., Vibration RMS exceeds 2.0 g - immediate shutdown]

## Pitfalls

- Never assign Severity 5 based on one parameter alone. Cross-validate with at least two sources.
- Temperature readings can be misleading in extreme ambient conditions. Ask for baseline-normalized values.
- Acoustic descriptions are subjective. Ask for noise type and whether continuous or intermittent.
- If sensor data is unavailable, rely on visual and oil condition as primary indicators.
- Do not conflate oil change interval with oil health. New oil can still show high Fe ppm.

## Verification

After generating the report, confirm with the user:
- Does the severity match their on-site observations?
- Are escalation thresholds feasible for their monitoring setup?
- Are there additional data points (CMS trending, historical Fe ppm) that could refine the assessment?
