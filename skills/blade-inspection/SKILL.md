---
name: wind-turbine-blade-inspection
description: Assesses wind turbine blade condition from visual inspection data. Classifies damage type and severity (1-5) across seven failure modes and recommends repair or operational actions.
version: 1.0.0
author: Sertug17
license: MIT
metadata:
  hermes:
    tags: [Energy, Maintenance, Wind-Turbine, Blade, Drone-Inspection, Erosion, Lightning, Structural, Debonding]
    related_skills: [wind-turbine-gearbox]
---

# Wind Turbine Blade Inspection Intelligence

Evaluates blade condition from drone or ground-based visual inspection and produces a structured damage assessment across seven failure modes.

## When to Use

Load this skill when the user wants to:
- Assess blade health from drone inspection images or written findings
- Classify damage type and severity on a 1-5 scale per blade and per zone
- Determine whether a turbine should continue operating, be scheduled for repair, or shut down
- Generate a structured blade inspection report with repair recommendations

## Blade Zones

| Zone | Span     | Description |
|------|----------|-------------|
| Root | 0-33%    | Highest structural loads, bolted connection area |
| Mid  | 33-66%   | Transition zone, moderate aerodynamic load |
| Tip  | 66-100%  | Highest velocity, most erosion-prone, lightning receptor area |

Surfaces: Leading Edge (LE), Trailing Edge (TE), Suction Side (SS), Pressure Side (PS)

## Damage Type Definitions

| Damage Type            | Description                                          | Typical Location        |
|------------------------|------------------------------------------------------|-------------------------|
| Surface crack          | Gelcoat or laminate cracks, linear fractures         | LE, TE, root transition |
| Erosion / wear         | Material loss, pitting, roughening                   | LE tip zone             |
| Lightning damage       | Burn marks, punctures, receptor damage               | Tip, receptor area      |
| Lamination/structural  | Delamination, fiber exposure, buckling, dents        | Any zone                |
| Debonding              | Bond line separation at LE, TE, or shear web         | LE, TE, internal        |
| Ice accumulation       | Ice buildup on surface or edges                      | Any zone                |
| General visual anomaly | Discoloration, contamination, coating loss           | Any zone                |

## Severity Scale

| Severity | Label       | Description                                         | Action                            |
|----------|-------------|-----------------------------------------------------|-----------------------------------|
| 1        | Healthy     | No damage or cosmetic marks only                    | Continue normal operation         |
| 2        | Minor       | Early erosion, superficial cracks, coating loss     | Increase inspection frequency     |
| 3        | Moderate    | Gelcoat breach, early debonding, defined damage     | Repair within 1-3 months          |
| 4        | Significant | Structural involvement, active debonding, lightning | Repair within 2-4 weeks           |
| 5        | Critical    | Fiber exposure, structural breach, delamination     | Immediate shutdown required       |

## Procedure

1. Collect inputs: blade IDs, inspection method, findings per blade per zone per surface.
2. Classify each finding by damage type.
3. Assign severity per finding using the severity scale.
4. Determine overall blade severity as the highest finding for that blade.
5. Determine turbine-level severity as the highest across all blades.
6. Apply damage-specific rules:
   - Lightning damage: minimum Severity 4 until OEM confirms otherwise.
   - Debonding at LE or TE over 300 mm: escalate to Severity 4.
   - Any confirmed fiber exposure: minimum Severity 4.
   - Erosion with full gelcoat loss over 500 mm span at tip: Severity 4.
   - Active ice accumulation: always Severity 4.
7. Generate output report using the format below.

## Output Format

=== BLADE INSPECTION REPORT ===

ASSET        : [Turbine ID]
SITE         : [Site name]
INSPECTION   : [Date / Method]
BLADES       : [Number inspected]

BLADE [ID]:
  Zone/Surface  : [e.g., Tip / Leading Edge]
  Damage Type   : [e.g., Erosion]
  Description   : [e.g., Deep pitting ~600 mm span, gelcoat fully lost]
  Severity      : [1-5] - [Label]

BLADE [ID] OVERALL SEVERITY: [1-5] - [Label]

TURBINE-LEVEL SEVERITY : [1-5] - [Label]
SHUTDOWN RECOMMENDATION: [Yes / No / Conditional]

REPAIR PRIORITY:
  - [e.g., Blade 2 tip LE erosion - schedule LEP repair within 6 weeks]

MONITORING STRATEGY:
  - [e.g., Monthly drone re-inspection for all blades]

ESCALATION TRIGGERS:
  - [e.g., Debond length exceeds 500 mm - shutdown for repair]
  - [e.g., SCADA vibration or imbalance alarms - ground turbine]

## Damage-Specific Guidance

Erosion: Progresses from roughening to pitting to gelcoat loss to fiber exposure. Repair with Leading Edge Protection (LEP) tape or coating. Severity 3-4 causes measurable energy production loss.

Lightning: Always notify OEM. Minor visible damage may hide internal delamination. Do not assume safe to operate until specialist confirms.

Debonding: LE debonding causes aerodynamic noise and vibration. TE debonding starts at tip and progresses toward root. Bond line gap over 300 mm is Severity 4.

Lamination/Structural: Fiber exposure is always Severity 4 minimum. Dents or buckling without fiber exposure is Severity 3.

Ice: Active ice requires immediate grounding due to rotor imbalance and ice throw risk. After melting, inspect surface for underlying damage.

## Pitfalls

- Do not classify erosion from low-resolution images. Ask for close-up zone-specific photos.
- Lightning damage is always higher priority than it looks. Treat as Severity 4 until proven otherwise.
- Debonding can be invisible from drone imagery. If SCADA shows imbalance alarms, flag potential hidden debonding.
- Active ice is a safety hazard. Recommend immediate grounding.
- Assess each blade independently. Damage distribution is rarely uniform across all three blades.

## Verification

After generating the report, confirm with the user:
- Does the severity match the inspector's on-site assessment?
- Are all three blades accounted for?
- Are there SCADA alarms (vibration, imbalance, power curve deviation) correlating with findings?
- Is there a previous inspection report for trend comparison?
