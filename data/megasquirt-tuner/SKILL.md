---
name: megasquirt-tuner
description: "Megasquirt ECU tuning and calibration using TunerStudio. Use when
  working with Megasquirt engine management systems for: (1) VE table tuning and
  fuel map optimization, (2) Ignition timing maps and spark advance, (3) Idle
  control and warmup enrichment, (4) AFR target tuning and closed-loop feedback,
  (5) Sensor calibration (TPS, MAP, CLT, IAT, O2), (6) Acceleration enrichment
  and deceleration fuel cut, (7) Boost control and launch control setup, (8)
  Datalog analysis and troubleshooting, (9) Base engine configuration and
  injector setup, (10) MSQ tune file analysis and safety review, (11) Any
  Megasquirt/TunerStudio ECU tuning tasks."
---


# Megasquirt ECU Tuning with TunerStudio

Guidance for tuning Megasquirt engine management systems using TunerStudio software.

## Core Concepts

### Required Fuel Equation
Megasquirt calculates fuel delivery using:
```
Pulse Width = Required Fuel × VE% × MAP × AFR Target Correction × Air Density × Warmup × Accel Enrichment × Other Corrections
```

**Required Fuel** is the base injector pulse width at 100% VE, 100kPa MAP, standard temperature.

### Key Tuning Tables

| Table | Purpose | Typical Resolution |
|-------|---------|-------------------|
| VE Table | Volumetric efficiency vs RPM/MAP | 16×16 or 12×12 |
| AFR Target | Desired air-fuel ratio vs RPM/MAP | 12×12 |
| Spark Advance | Ignition timing vs RPM/MAP | 12×12 or 16×16 |
| Warmup Enrichment | Fuel correction vs coolant temp | 10-20 points |
| TPS-based Accel | Accel enrichment vs TPSdot | 10-20 points |
| MAP-based Accel | Accel enrichment vs MAPdot | 10-20 points |

## Tuning Workflow

### 1. Base Configuration
Before tuning, verify:
- Engine displacement and cylinder count
- Injector flow rate (cc/min or lb/hr)
- Injector staging (simultaneous, alternating, sequential)
- Required Fuel calculation matches injector size
- Ignition input/output settings match hardware
- Trigger wheel and ignition mode configured

### 2. Sensor Calibration
Calibrate sensors before tuning:
- **CLT (Coolant Temp)**: Set resistance values at known temps
- **IAT (Intake Air Temp)**: Similar to CLT
- **TPS**: Set closed and WOT positions (0-100%)
- **MAP**: Verify atmospheric reading at key-on
- **O2 Sensor**: Calibrate wideband controller output range

### 3. VE Table Tuning (Speed Density)

**Method 1: Wideband O2 Feedback**
1. Enable EGO correction with moderate authority (±15-20%)
2. Set realistic AFR targets
3. Run engine at steady state (fixed RPM/load cell)
4. Allow EGO to correct, note correction percentage
5. Adjust VE by inverse of correction (if +10% correction, increase VE by 10%)
6. Save and move to next cell

**Method 2: Calculate from Measured AFR**
```
New VE = Current VE × (Measured AFR / Target AFR)
```

**Tuning Order:**
1. Start with idle region (600-1000 RPM, 30-50kPa)
2. Light cruise (1500-2500 RPM, 40-60kPa)
3. Part throttle acceleration
4. WOT high load
5. Transition regions

### 4. AFR Target Table

Set targets based on application:

| Condition | Target AFR | Lambda |
|-----------|-----------|--------|
| Idle | 13.5-14.5 | 0.92-0.99 |
| Light Cruise | 14.5-15.5 | 0.99-1.06 |
| Part Throttle | 13.5-14.5 | 0.92-0.99 |
| WOT Naturally Aspirated | 12.5-13.0 | 0.85-0.88 |
| WOT Turbo/Supercharged | 11.5-12.5 | 0.78-0.85 |

### 5. Ignition Timing

**Base Settings:**
- Set cranking advance (typically 10-20° BTDC)
- Set idle advance (typically 15-25° BTDC)
- Build spark table following engine-specific guidelines

**Typical Spark Advance Table (Naturally Aspirated):**
- Low RPM/High Load: 10-20°
- Low RPM/Low Load: 25-35°
- High RPM/High Load: 25-35°
- High RPM/Low Load: 35-45°

**Knock Considerations:**
- Reduce timing 1-2° at a time if knock detected
- Add more fuel in knock-prone areas
- Use knock sensor feedback if available

### 6. Idle Control

**Idle Valve PWM Settings:**
- Closed position: PWM at hot idle (typically 20-40%)
- Open position: PWM for cold start (typically 60-80%)
- Cranking position: PWM during start (typically 50-70%)

**Idle Target RPM Table:**
- Hot: 700-900 RPM
- Cold (0°C): 1200-1500 RPM
- Interpolate between

### 7. Warmup Enrichment

**Afterstart Enrichment:**
- Duration: 30-200 cycles (engine revolutions)
- Amount: 20-40% additional fuel
- Taper to zero over duration

**Warmup Enrichment Curve:**
- -40°C: 150-200%
- 0°C: 120-140%
- 70°C (operating): 100%

### 8. Acceleration Enrichment

**TPS-based (Alpha-N blending):**
- Threshold: 5-10%/sec TPSdot
- Enrichment: 10-30% added fuel
- Decay: 0.5-2 seconds

**MAP-based (for MAP-dot systems):**
- Threshold: 10-30 kPa/sec
- Enrichment scales with rate of change

**Cold Multiplier:**
- Increase accel enrichment when cold (1.5-3× at -20°C)

## Advanced Features

### Boost Control

**Open Loop:**
- Duty cycle table vs RPM/target boost

**Closed Loop (if supported):**
- PID parameters for wastegate control
- Target boost table vs RPM/gear

### Launch Control

- Set RPM limit (typically 4000-6000 RPM)
- Configure retard timing during launch (0-10° BTDC)
- Set fuel/ignition cut method

### Flat Shift

- Maintain throttle during shifts
- Brief fuel/ignition cut at shift point
- Retain boost between gears

## Datalog Analysis

### Key Parameters to Log

| Parameter | What to Watch |
|-----------|---------------|
| RPM | Stability, limiter hits |
| MAP | Response to throttle, leaks |
| AFR (wideband) | Deviation from target |
| EGO Correction | Should stay within ±10% |
| CLT | Reaches operating temp |
| IAT | Heat soak effects |
| Spark Advance | Matches table |
| Injector PW | Headroom, max duty cycle |
| TPS | Smooth operation, TPSdot |

### Common Issues

**Lean at Tip-In:**
- Increase TPS-based accel enrichment
- Check MAPdot sensitivity

**Rich at Decel:**
- Enable deceleration fuel cut (DFCO)
- Set appropriate TPS threshold (typically <10%)
- Set RPM threshold above idle

**Idle Hunting:**
- Check for vacuum leaks
- Adjust idle PID gains
- Verify TPS closed position
- Check ignition timing stability

**Knock at High Load:**
- Reduce spark advance in affected cells
- Enrich mixture (reduce target AFR)

## TunerStudio Specific

### Project Setup
1. Create new project → select firmware (MS1, MS2, MS3)
2. Load base tune (.msq file) or start from default
3. Connect to controller (serial, USB, or Bluetooth)
4. Sync with controller to load current settings

### Tuning Interface
- **Basic/Customize Tuning**: Navigate tables
- **Table**: View/edit individual tables
- **Runtime Data**: Real-time monitoring
- **Datalog**: Record and playback logs

### Auto-Tune
- Enable VEAL (VE Analyze Live) with wideband
- Set acceptable AFR range
- Drive through as many cells as possible
- Review and accept changes
- Disable when done

### Safety Limits

**Rev Limiter:**
- Soft limit: retard timing
- Hard limit: fuel/ignition cut
- Set 200-500 RPM above max desired

**Overboost Protection:**
- Fuel cut above target pressure
- Ignition cut option

**Lean Cut:**
- Disable injectors if AFR exceeds safe threshold
- Typically 15:1+ under load

## MSQ Tune File Analysis

The skill can analyze `.msq` tune files to identify safety issues, optimization opportunities, and configuration problems.

### Using the Analyzer

Run the analysis script on any MSQ file:

```bash
python3 scripts/analyze_msq.py your_tune.msq
```

Or provide the tune file content directly for analysis.

### How to Provide the MSQ File

**Option 1: Paste the file content** (Recommended)
- Open the `.msq` file in a text editor (it's plain text)
- Copy the entire content
- Paste it directly into the chat: "Analyze this MSQ file: [paste content]"

**Option 2: Upload the file**
- If your chat interface supports file attachments, attach the `.msq` file directly
- The skill will read and analyze it

**Option 3: Provide a file path** (if running locally)
```bash
python3 scripts/analyze_msq.py /path/to/your/tune.msq
```

**Security Restrictions for Script Usage:**
- Only files with `.msq` extension are accepted
- Path traversal sequences (`../`) are blocked
- Symbolic links are not allowed
- File must be a regular text file (not binary)

**Option 4: Share key sections**
If the file is large, paste specific sections you're concerned about:
- `[veTable1]` section for fuel map review
- `[sparkTable1]` for ignition timing
- `[afrTable1]` for AFR targets
- `[revLimiter]` for safety limits

### Example Prompts

```
"Review this MSQ file for safety issues before I start my engine: [paste content]"

"Check my VE table - does anything look suspicious? [paste veTable section]"

"Analyze my ignition timing map for knock risk: [paste sparkTable section]"

"I just updated my AFR targets, review them: [paste afrTable section]"
```

### What Gets Analyzed

**Safety Checks:**
- 🚨 **Critical**: AFR targets that could cause engine damage, excessive ignition timing
- ⚠️ **Warnings**: Rev limiter not configured, suspicious VE values, high injector duty

**Configuration Review:**
- Required fuel calculation sanity check
- VE table range and smoothness
- AFR target appropriateness for NA vs forced induction
- Ignition timing ranges and knock risk assessment
- Cranking pulse widths
- Warmup enrichment curve
- Safety limits (rev limiter, overboost)

**Optimization Opportunities:**
- Injector duty cycle headroom
- VE table smoothness (sudden jumps)
- Conservative vs aggressive timing maps

### Interpreting Results

**Example Analysis Output:**
```
📋 VE Table
----------------------------------------
  ⚠️ VE table has very low values (15.0) - check for empty/untuned cells
  📊 12 cells have >30% jumps from neighbors - consider smoothing
  ✓ VE table range: 15.0 - 105.0 (avg: 62.3)

📋 Ignition Timing
----------------------------------------
  ⚠️ High ignition advance (48°) - verify on dyno with knock detection
  ✓ Spark advance range: 8° - 48° BTDC

SUMMARY
============================================================
🚨 CRITICAL ISSUES: 0
⚠️  WARNINGS: 2
✓ Suggestions: 4
ℹ️  Notes: 1
```

### Common Issues Detected

**High Priority:**
- No rev limiter configured
- Lean AFR targets under load (>14.0:1 at WOT)
- Ignition timing >45° (severe knock risk)
- Estimated injector duty >90%

**Medium Priority:**
- VE values <20 or >120
- Large jumps between adjacent cells (>30%)
- Missing warmup enrichment taper
- Cranking PW too high/low for conditions

**Low Priority:**
- Conservative timing that may leave power on table
- Overly rich AFR targets
- Excessive injector headroom

### Tune Review Workflow

1. **Before First Start:**
   ```
   You: "Review this base tune before I start the engine"
   AI: [Runs analysis, flags safety issues]
   ```

2. **After Changes:**
   ```
   You: "I just updated my VE table, check it"
   AI: [Analyzes for anomalies, suggests smoothing]
   ```

3. **Before Dyno/Track:**
   ```
   You: "Review my tune before high load testing"
   AI: [Checks timing, AFR, safety limits, injector headroom]
   ```

## Reference Materials

For detailed documentation, see:
- [references/tunerstudio-reference.md](references/tunerstudio-reference.md) - Full TunerStudio documentation
- [references/megasquirt-tuning-guide.md](references/megasquirt-tuning-guide.md) - Comprehensive tuning procedures

## Quick Reference Formulas

**Injector Duty Cycle:**
```
DC% = (Injector PW / Injection Period) × 100
```
Keep under 85% for safety margin.

**Required Fuel Calculation:**
```
Required Fuel (ms) = (Engine CC × 5) / (Number of Injectors × Injector CC/Min) × 2
```
(The ×2 accounts for 2 rotations per cycle)

**Airflow Estimation:**
```
MAF (g/s) ≈ (RPM × Displacement × VE% × MAP/100) / (2 × 60 × R × Temp)
```

## Safety Checklist

Before starting engine:
- [ ] Injector flow rate correct in settings
- [ ] Ignition timing verified with timing light
- [ ] Fuel pump primes and holds pressure
- [ ] No fuel leaks
- [ ] Wideband O2 sensor warmed up
- [ ] Emergency fuel/ignition cut accessible

During tuning:
- [ ] Monitor EGT if available
- [ ] Listen for detonation/knock
- [ ] Watch AFR on transitions
- [ ] Keep VE table changes conservative
- [ ] Save tune frequently with version notes
