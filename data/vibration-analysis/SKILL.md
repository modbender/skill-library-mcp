---
name: wind-turbine-vibration-analysis
description: Analyzes wind turbine drivetrain vibration data (main bearing, gearbox, generator) from CMS trends, RMS/peak values, frequency spectrum, and SCADA alarms. Classifies severity (1-5) and recommends shutdown or monitoring actions.
version: 1.0.0
author: Sertug17
license: MIT
metadata:
  hermes:
    tags: [Energy, Maintenance, Wind-Turbine, Vibration, CMS, Drivetrain, Gearbox, Generator, Bearing, Spectrum-Analysis]
    related_skills: [wind-turbine-gearbox, wind-turbine-blade-inspection]
---

# Wind Turbine Drivetrain Vibration Analysis

Evaluates drivetrain vibration health across three subsystems: main bearing, gearbox, and generator.

## When to Use

Load this skill when the user wants to:
- Assess drivetrain vibration health from CMS or SCADA data
- Interpret RMS, peak-to-peak, or spectral findings for main bearing, gearbox, or generator
- Correlate vibration alarms with operational events
- Decide whether to continue operating, increase monitoring, or shut down

## Drivetrain Components

| Component | Sensor Location | Key Frequencies |
|-----------|----------------|-----------------|
| Main Bearing | Non-drive end, drive end | BPFO, BPFI, BSF, FTF |
| Gearbox LSS | Low speed shaft | Gear mesh (LSS x teeth), bearing defect freqs |
| Gearbox IMS | Intermediate shaft | IMS gear mesh harmonics |
| Gearbox HSS | High speed shaft | HSS gear mesh, bearing defect freqs |
| Generator NDE | Non-drive end bearing | Electrical harmonics, bearing defect freqs |
| Generator DE | Drive end bearing | Bearing defect freqs, rotor unbalance |

## Vibration Thresholds (ISO 10816 / CMS Reference)

| Location | Normal | Warning | Critical |
|----------|--------|---------|----------|
| Main Bearing RMS (g) | < 0.3 | 0.3 - 0.8 | > 0.8 |
| Gearbox HSS RMS (g) | < 0.5 | 0.5 - 1.5 | > 1.5 |
| Gearbox LSS/IMS RMS (g) | < 0.3 | 0.3 - 1.0 | > 1.0 |
| Generator RMS (g) | < 0.5 | 0.5 - 1.2 | > 1.2 |
| Peak-to-peak step change | < 10% | 10-30% | > 30% |

Note: Always evaluate against site-specific baseline. A 20% rise from stable baseline is more significant than an absolute value alone.

## Frequency Fault Signatures

| Fault | Frequency Signature |
|-------|-------------------|
| Bearing outer race (BPFO) | (N/2) x (1 - d/D x cos a) x RPM |
| Bearing inner race (BPFI) | (N/2) x (1 + d/D x cos a) x RPM |
| Gear mesh | number of teeth x shaft RPM |
| Gear mesh sidebands | GMF +/- shaft frequency |
| Rotor unbalance | 1x RPM dominant |
| Misalignment | 2x RPM dominant, axial component |
| Looseness | Sub-harmonics (0.5x, 1.5x) or high harmonic content |

## Severity Scale

| Severity | Label | Description | Action |
|----------|-------|-------------|--------|
| 1 | Healthy | All values normal, stable trend | Continue normal operation |
| 2 | Early warning | 1-2 parameters in warning zone, stable | Increase CMS polling frequency |
| 3 | Moderate | Multiple warning flags or single critical | Inspect within 2 weeks |
| 4 | Significant | Critical zone or rapid trend growth | Plan shutdown within 48-72 hours |
| 5 | Critical | Multiple critical flags, step-change | Immediate shutdown required |

## Procedure

1. Collect inputs: CMS trend (last 30-90 days), current RMS and peak-to-peak per component, frequency spectrum findings, SCADA alarms, operational context.
2. Evaluate RMS values against thresholds. Flag Warning or Critical zones.
3. Analyze trend:
   - Stable: value in warning zone but flat for >30 days = lower urgency
   - Gradual rise: value increasing steadily = schedule inspection
   - Step change: sudden jump >30% = treat as Critical regardless of absolute value
4. Interpret frequency spectrum if available:
   - Match dominant peaks to fault signatures table
   - Note sidebands around gear mesh frequencies
   - Note sub-harmonics or 1x/2x dominance
5. Correlate with SCADA alarms and operational events.
6. Assign severity per component, then determine drivetrain-level severity as highest.
7. Generate output report using the format below.

## Output Format

=== DRIVETRAIN VIBRATION REPORT ===

ASSET        : [Turbine ID]
SITE         : [Site name]
DATA PERIOD  : [Date range of CMS/SCADA data]
MISSING DATA : [List any unavailable inputs]

MAIN BEARING:
  RMS          : [value] g - [Normal / Warning / Critical]
  Trend        : [Stable / Gradual rise / Step change]
  Spectrum     : [Key findings or not available]
  SCADA Alarms : [Count and type]
  Severity     : [1-5] - [Label]

GEARBOX (LSS / IMS / HSS):
  RMS          : LSS [value] g / IMS [value] g / HSS [value] g
  Trend        : [per shaft]
  Spectrum     : [Key findings]
  SCADA Alarms : [Count and type]
  Severity     : [1-5] - [Label]

GENERATOR (DE / NDE):
  RMS          : DE [value] g / NDE [value] g
  Trend        : [per bearing]
  Spectrum     : [Key findings]
  SCADA Alarms : [Count and type]
  Severity     : [1-5] - [Label]

DRIVETRAIN SEVERITY : [1-5] - [Label]
SHUTDOWN            : [Yes / No / Conditional]

FAULT HYPOTHESIS:
  - [e.g., HSS bearing outer race defect - BPFO peak confirmed at X Hz]
  - [e.g., Gear mesh sideband modulation - possible gear wear or load variation]

RECOMMENDED ACTIONS:
  - [e.g., Increase CMS polling to daily for HSS channel]
  - [e.g., Oil sample with ferrography within 72 hours]
  - [e.g., Plan HSS bearing replacement at next scheduled outage]

ESCALATION TRIGGERS:
  - [e.g., RMS exceeds 1.5 g on HSS - immediate shutdown]
  - [e.g., Step change >30% on any channel - treat as critical]
  - [e.g., New BPFO or BPFI peak confirmed in spectrum - escalate to Severity 4]

## Cross-Skill Correlation

If gearbox visual data is available, load wind-turbine-gearbox skill and cross-correlate:
- High Fe ppm + rising HSS vibration = active wear confirmation
- Spalling in borescope + BPFO peak in spectrum = bearing failure progression
- Normal oil + rising vibration = early fault not yet generating debris (higher urgency)

If blade inspection data is available, check for rotor imbalance:
- 1x RPM dominant in main bearing spectrum + blade damage = aerodynamic imbalance
- Asymmetric blade damage across A/B/C = mass or aerodynamic imbalance source

## Pitfalls

- Do not evaluate vibration in isolation. Cross-reference with oil analysis and visual inspection.
- A single high RMS reading during a storm or grid fault is not a fault indicator. Check operational context.
- Spectrum analysis requires RPM-normalized data. Raw frequency peaks are meaningless without shaft RPM.
- Generator electrical faults can appear as vibration. Check electrical data before attributing to mechanical cause.
- Stable high RMS is less urgent than rapidly rising moderate RMS. Trend rate matters more than absolute value.

## Verification

After generating the report, confirm with the user:
- Does the severity match CMS system alerts or OEM recommendations?
- Is shaft RPM data available to normalize spectrum frequencies?
- Are there recent maintenance events that could explain vibration changes?
- Is SCADA power curve deviation consistent with vibration findings?
