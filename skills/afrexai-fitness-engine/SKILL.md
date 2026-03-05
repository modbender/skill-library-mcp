# Fitness & Training Engineering

> Complete periodized training system — program design, progressive overload, recovery optimization, body composition, and race prep. Works for any goal: strength, hypertrophy, endurance, hybrid (Hyrox/CrossFit), or general fitness. Zero dependencies.

## Quick Health Check

Run `/fitness-check` on any training program. Score each signal 0–2:

| # | Signal | 0 (Red) | 1 (Yellow) | 2 (Green) |
|---|--------|---------|------------|-----------|
| 1 | Progressive overload | No tracking, random weights | Some tracking, inconsistent | Logged every session, planned progression |
| 2 | Program structure | No plan, different every day | Loosely follows a split | Periodized with mesocycles |
| 3 | Recovery management | <6h sleep, no rest days | Some rest, inconsistent sleep | 7-9h sleep, planned deloads |
| 4 | Nutrition alignment | No macro awareness | Tracks sometimes | Protein target hit daily |
| 5 | Movement quality | Pain during lifts, no warmup | Occasional warmup, some issues | Full warmup, pain-free movement |
| 6 | Balance | All push, no pull; all upper, no lower | Minor imbalances | Push/pull/legs balanced, mobility included |
| 7 | Consistency | <2x/week or constantly changing | 3x/week with gaps | 3-6x/week sustained >8 weeks |
| 8 | Goal specificity | No clear goal | Vague goal ("get fit") | SMART goal with timeline |

**Score: /16** → 0-5: Complete redesign needed | 6-10: Fix gaps first | 11-14: Optimize details | 15-16: Elite — maintain and periodize

---

## Phase 1: Athlete Assessment

### Training Brief YAML

```yaml
athlete_brief:
  name: ""
  age: 0
  sex: "M/F"
  height_cm: 0
  weight_kg: 0
  body_fat_pct: 0  # estimate if unknown
  training_age_years: 0  # years of consistent training
  
  goals:
    primary: ""  # strength / hypertrophy / fat loss / endurance / hybrid / general fitness
    secondary: ""
    target_event: ""  # e.g., "Hyrox London — June 2026"
    timeline_weeks: 0
  
  current_training:
    frequency_per_week: 0
    session_duration_min: 0
    current_program: ""
    training_history: ""  # brief summary of last 6-12 months
  
  benchmarks:  # current 1RM or best effort
    squat_kg: 0
    bench_kg: 0
    deadlift_kg: 0
    overhead_press_kg: 0
    pull_ups: 0
    run_5k_min: 0
    run_10k_min: 0
    row_1000m_sec: 0
  
  constraints:
    injuries: []
    equipment_available: ""  # full gym / home gym / bodyweight / limited
    schedule_constraints: ""
    nutrition_approach: ""  # tracking macros / intuitive / specific diet
  
  lifestyle:
    sleep_hours: 0
    stress_level: "low/moderate/high"
    occupation_activity: "sedentary/light/moderate/active"
    steps_per_day: 0
```

### Training Age Classification

| Level | Training Age | Characteristics | Progression Rate |
|-------|-------------|-----------------|-----------------|
| Beginner | 0-12 months | Rapid neural adaptation, learning movement patterns | 2-5 kg/week on compounds |
| Intermediate | 1-3 years | Slower gains, needs periodization | 1-2 kg/month on compounds |
| Advanced | 3-7 years | Marginal gains, advanced programming required | 1-5 kg per training block |
| Elite | 7+ years | Near genetic ceiling, micro-periodization | Competition-cycle gains only |

### Goal-Specific Focus

| Goal | Volume Priority | Intensity Priority | Cardio | Nutrition |
|------|----------------|-------------------|--------|-----------|
| Strength | Moderate (3-5 sets) | High (80-95% 1RM) | Minimal | Surplus or maintenance |
| Hypertrophy | High (10-20 sets/muscle/week) | Moderate (60-80% 1RM) | Low-moderate | Surplus (+300-500 cal) |
| Fat loss | Moderate-high (maintain muscle) | Moderate-high (keep strength) | Moderate-high | Deficit (-300-500 cal) |
| Endurance | Low-moderate (2-3 strength sessions) | Moderate | High priority | Maintenance or slight surplus |
| Hybrid (Hyrox) | Moderate | Moderate | High — mixed modalities | Maintenance to slight surplus |
| General fitness | Moderate | Moderate | Moderate | Maintenance |

---

## Phase 2: Program Architecture

### Periodization Models

| Model | Best For | Structure | When to Use |
|-------|---------|-----------|-------------|
| Linear | Beginners | Increase load weekly | First 6-12 months |
| Undulating (DUP) | Intermediate | Vary rep ranges within week | Stalling on linear |
| Block | Advanced | 3-4 week focused blocks | Peaking for competition |
| Conjugate | Advanced strength | Max effort + dynamic effort rotation | Powerlifting focus |
| Hybrid periodization | Hybrid athletes | Concurrent strength + cardio blocks | Hyrox, CrossFit, OCR |

### Mesocycle Template YAML

```yaml
mesocycle:
  name: "Hypertrophy Block 1"
  duration_weeks: 4
  goal: "hypertrophy"
  
  week_1:  # Introductory
    intensity_rpe: "6-7"
    volume_modifier: 0.85  # 85% of peak volume
    notes: "Focus on technique, establish baseline"
  
  week_2:  # Building
    intensity_rpe: "7-8"
    volume_modifier: 0.95
    notes: "Push volume up"
  
  week_3:  # Overreaching
    intensity_rpe: "8-9"
    volume_modifier: 1.0  # Peak volume
    notes: "Hardest week — expect fatigue"
  
  week_4:  # Deload
    intensity_rpe: "5-6"
    volume_modifier: 0.60
    notes: "Cut volume 40%, maintain intensity, recover"
  
  progression_rule: "Add 2.5kg to compounds or 1-2 reps at same weight"
  deload_frequency: "Every 4th week (beginners: every 6-8 weeks)"
```

### Training Split Selection

| Split | Frequency | Best For | Sessions/Week |
|-------|-----------|---------|---------------|
| Full Body | 3x/week | Beginners, time-limited | 3 |
| Upper/Lower | 4x/week | Intermediates, balanced | 4 |
| Push/Pull/Legs | 5-6x/week | Intermediates-advanced, hypertrophy | 5-6 |
| Bro Split | 5x/week | Advanced bodybuilding | 5 |
| Upper/Lower + Conditioning | 5x/week | Hybrid athletes | 3 lifting + 2 conditioning |
| Concurrent | 5-6x/week | Hyrox/OCR/CrossFit | Mixed daily |

**Selection Rules:**
1. Beginners: Full body 3x/week. Always.
2. If <4 days available: Full body or upper/lower
3. If hypertrophy focus: PPL or upper/lower for volume
4. If hybrid/endurance: Upper/lower + dedicated conditioning days
5. Recovery capacity determines frequency — more isn't always better

---

## Phase 3: Exercise Selection & Programming

### Movement Pattern Requirements

Every program MUST include these patterns weekly:

| Pattern | Primary Exercises | Alternatives (limited equipment) |
|---------|------------------|----------------------------------|
| Horizontal Push | Bench press, dumbbell press | Push-ups, floor press |
| Horizontal Pull | Barbell row, cable row | Inverted rows, resistance band rows |
| Vertical Push | Overhead press, dumbbell shoulder press | Pike push-ups, handstand push-ups |
| Vertical Pull | Pull-ups, lat pulldown | Band pull-ups, doorframe rows |
| Squat | Back squat, front squat, goblet squat | Pistol squats, Bulgarian split squats |
| Hinge | Deadlift, Romanian deadlift, hip thrust | Single-leg RDL, KB swings |
| Carry/Core | Farmer walks, pallof press, hanging leg raise | Plank variations, dead bugs |
| Lunge/Single-leg | Walking lunges, step-ups | Bodyweight lunges, single-leg glute bridge |

### Rep Range Guide

| Goal | Reps | Sets/Exercise | Rest | RPE Target |
|------|------|--------------|------|------------|
| Strength | 1-5 | 3-5 | 3-5 min | 8-9.5 |
| Hypertrophy | 6-12 | 3-4 | 60-120 sec | 7-9 |
| Muscular endurance | 12-20+ | 2-3 | 30-60 sec | 7-8 |
| Power | 1-5 | 3-5 | 3-5 min | 7-8 (explosive) |

### RPE Scale Reference

| RPE | Description | Reps in Reserve |
|-----|-------------|----------------|
| 10 | Maximum effort, cannot do another rep | 0 RIR |
| 9 | Could maybe do 1 more | 1 RIR |
| 8 | Could do 2 more | 2 RIR |
| 7 | Could do 3 more, moderate effort | 3 RIR |
| 6 | Light, warmup weight feel | 4+ RIR |

### Progressive Overload Methods (Priority Order)

1. **Add reps** — Hit top of rep range? Add 1-2 reps next session
2. **Add weight** — Hit top of rep range for all sets? Add 2.5-5 kg
3. **Add sets** — Within weekly volume targets? Add 1 set
4. **Increase ROM** — Deficit deadlifts, paused squats, deeper squats
5. **Decrease rest** — Only for conditioning/endurance goals
6. **Increase tempo** — Slower eccentrics (3-4 sec) for hypertrophy
7. **Increase frequency** — Train muscle group more often within recovery limits

### Weekly Volume Landmarks (Sets Per Muscle Group Per Week)

| Muscle Group | MEV (Minimum) | MAV (Maximum Adaptive) | MRV (Maximum Recoverable) |
|-------------|---------------|----------------------|--------------------------|
| Chest | 8 | 12-16 | 20-22 |
| Back | 8 | 12-18 | 20-25 |
| Shoulders | 6 | 10-14 | 18-20 |
| Quads | 6 | 10-16 | 18-20 |
| Hamstrings | 4 | 8-12 | 14-16 |
| Biceps | 4 | 8-14 | 16-20 |
| Triceps | 4 | 8-12 | 14-18 |
| Glutes | 4 | 8-14 | 16-20 |
| Calves | 6 | 10-14 | 16-20 |
| Abs | 0 | 6-10 | 14-16 |

**Rules:**
- Start at MEV, add 1-2 sets/muscle/week across mesocycle
- When gains stall, check if approaching MRV (fatigue masking gains)
- Deload resets fatigue — return to MEV and progress again
- Compounds count toward multiple muscle groups (bench = chest + triceps + shoulders)

---

## Phase 4: Sample Programs

### Beginner Full Body (3x/week)

```yaml
program:
  name: "Beginner Full Body"
  level: "beginner"
  frequency: "3x/week (Mon/Wed/Fri)"
  duration: "12 weeks"
  
  day_a:
    name: "Full Body A"
    exercises:
      - { name: "Barbell Back Squat", sets: 3, reps: "5", progression: "+2.5kg/session" }
      - { name: "Bench Press", sets: 3, reps: "5", progression: "+2.5kg/session" }
      - { name: "Barbell Row", sets: 3, reps: "8", progression: "+2.5kg/session" }
      - { name: "Dumbbell Shoulder Press", sets: 3, reps: "10", progression: "+1kg when 3x10" }
      - { name: "Plank", sets: 3, reps: "30-60 sec", progression: "+10 sec/week" }
  
  day_b:
    name: "Full Body B"
    exercises:
      - { name: "Deadlift", sets: 3, reps: "5", progression: "+5kg/session" }
      - { name: "Overhead Press", sets: 3, reps: "5", progression: "+2.5kg/session" }
      - { name: "Pull-ups (or lat pulldown)", sets: 3, reps: "AMRAP (or 8-10)", progression: "add reps → add weight" }
      - { name: "Romanian Deadlift", sets: 3, reps: "10", progression: "+2.5kg when 3x10" }
      - { name: "Hanging Leg Raise", sets: 3, reps: "10", progression: "+2 reps/week" }
  
  alternation: "A/B/A then B/A/B"
  warmup: "5 min cardio + movement-specific warmup sets"
  session_duration: "45-60 min"
```

### Intermediate Upper/Lower (4x/week)

```yaml
program:
  name: "Intermediate Upper/Lower"
  level: "intermediate"
  frequency: "4x/week"
  structure: "Upper A / Lower A / Rest / Upper B / Lower B / Rest / Rest"
  
  upper_a:  # Strength emphasis
    name: "Upper Strength"
    exercises:
      - { name: "Bench Press", sets: 4, reps: "4-6", rpe: 8 }
      - { name: "Weighted Pull-ups", sets: 4, reps: "4-6", rpe: 8 }
      - { name: "DB Shoulder Press", sets: 3, reps: "8-10", rpe: 8 }
      - { name: "Cable Row", sets: 3, reps: "8-10", rpe: 8 }
      - { name: "Lateral Raises", sets: 3, reps: "12-15", rpe: 8 }
      - { name: "Tricep Pushdowns", sets: 3, reps: "10-12", rpe: 8 }
      - { name: "Barbell Curls", sets: 3, reps: "10-12", rpe: 8 }
  
  lower_a:  # Quad emphasis
    name: "Lower Quad Focus"
    exercises:
      - { name: "Back Squat", sets: 4, reps: "4-6", rpe: 8 }
      - { name: "Romanian Deadlift", sets: 3, reps: "8-10", rpe: 8 }
      - { name: "Leg Press", sets: 3, reps: "10-12", rpe: 8 }
      - { name: "Walking Lunges", sets: 3, reps: "10/leg", rpe: 7 }
      - { name: "Leg Curl", sets: 3, reps: "10-12", rpe: 8 }
      - { name: "Calf Raises", sets: 4, reps: "12-15", rpe: 8 }
      - { name: "Pallof Press", sets: 3, reps: "10/side", rpe: 7 }
  
  upper_b:  # Volume emphasis
    name: "Upper Hypertrophy"
    exercises:
      - { name: "Overhead Press", sets: 4, reps: "6-8", rpe: 8 }
      - { name: "Lat Pulldown", sets: 4, reps: "8-10", rpe: 8 }
      - { name: "Incline DB Press", sets: 3, reps: "10-12", rpe: 8 }
      - { name: "Chest-Supported Row", sets: 3, reps: "10-12", rpe: 8 }
      - { name: "Face Pulls", sets: 3, reps: "15-20", rpe: 7 }
      - { name: "Hammer Curls", sets: 3, reps: "10-12", rpe: 8 }
      - { name: "Overhead Tricep Ext", sets: 3, reps: "10-12", rpe: 8 }
  
  lower_b:  # Posterior emphasis
    name: "Lower Posterior Focus"
    exercises:
      - { name: "Deadlift", sets: 4, reps: "3-5", rpe: 8 }
      - { name: "Front Squat", sets: 3, reps: "6-8", rpe: 8 }
      - { name: "Hip Thrust", sets: 3, reps: "8-10", rpe: 8 }
      - { name: "Bulgarian Split Squat", sets: 3, reps: "8/leg", rpe: 8 }
      - { name: "Nordic Curl (or leg curl)", sets: 3, reps: "6-10", rpe: 8 }
      - { name: "Standing Calf Raise", sets: 4, reps: "10-12", rpe: 8 }
      - { name: "Ab Wheel Rollout", sets: 3, reps: "8-12", rpe: 7 }
```

### Hyrox Training Program (5x/week)

```yaml
program:
  name: "Hyrox 12-Week Prep"
  level: "intermediate-advanced"
  frequency: "5x/week"
  structure: "Strength / Run + Stations / Active Recovery / Strength / Long Run + Stations"
  
  day_1:  # Monday — Strength
    name: "Functional Strength"
    exercises:
      - { name: "Back Squat", sets: 4, reps: "5", rpe: 8 }
      - { name: "Bench Press", sets: 4, reps: "5", rpe: 8 }
      - { name: "Weighted Pull-ups", sets: 4, reps: "6-8", rpe: 8 }
      - { name: "Farmer Walks", sets: 4, reps: "40m", weight: "32kg/hand" }
      - { name: "KB Swings", sets: 3, reps: "20", weight: "24kg" }
      - { name: "Sled Push", sets: 4, reps: "25m", rest: "90 sec" }
  
  day_2:  # Tuesday — Run + Stations
    name: "Race Simulation (Short)"
    warmup: "10 min easy jog"
    workout:
      - { segment: "Run", distance: "1km", pace: "race pace" }
      - { station: "Ski Erg", distance: "1000m" }
      - { segment: "Run", distance: "1km", pace: "race pace" }
      - { station: "Sled Push", distance: "50m" }
      - { segment: "Run", distance: "1km", pace: "race pace" }
      - { station: "Burpee Broad Jumps", reps: 80 }
      - { segment: "Run", distance: "1km", pace: "race pace" }
    cooldown: "10 min easy jog + stretch"
  
  day_3:  # Wednesday — Active Recovery
    name: "Recovery"
    workout:
      - { name: "Easy jog or walk", duration: "30-40 min", hr: "Zone 1-2" }
      - { name: "Foam rolling", duration: "15 min" }
      - { name: "Mobility work", duration: "15 min" }
  
  day_4:  # Thursday — Strength + Power
    name: "Power Endurance"
    exercises:
      - { name: "Deadlift", sets: 4, reps: "5", rpe: 8 }
      - { name: "Overhead Press", sets: 4, reps: "5", rpe: 8 }
      - { name: "Wall Balls", sets: 5, reps: "20", rest: "60 sec" }
      - { name: "Rowing Intervals", sets: 8, reps: "250m", rest: "60 sec" }
      - { name: "Lunges (weighted)", sets: 4, reps: "20m", weight: "16kg/hand" }
      - { name: "Sled Pull", sets: 4, reps: "25m", rest: "90 sec" }
  
  day_5:  # Saturday — Long Run + Stations
    name: "Race Simulation (Full)"
    warmup: "10 min easy jog"
    workout:
      - { segment: "Run", distance: "8km total (1km splits)", pace: "slightly above race pace" }
      - { note: "Insert one station after each 1km run — rotate through all 8 Hyrox stations" }
    stations_rotation:
      - "Ski Erg 1000m"
      - "Sled Push 50m"
      - "Sled Pull 50m"
      - "Burpee Broad Jumps 80m"
      - "Rowing 1000m"
      - "Farmer Carry 200m"
      - "Sandbag Lunges 100m"
      - "Wall Balls 100 reps"
    cooldown: "15 min easy jog + full stretch"

  hyrox_station_standards:
    ski_erg: "1000m"
    sled_push: "50m (152kg men / 102kg women)"
    sled_pull: "50m (103kg men / 78kg women)"
    burpee_broad_jumps: "80m"
    rowing: "1000m"
    farmer_carry: "200m (24kg men / 16kg women per hand)"
    sandbag_lunges: "100m (20kg men / 10kg women)"
    wall_balls: "100 reps (6kg men / 4kg women, 2.75m/2.44m target)"
  
  periodization_12_weeks:
    weeks_1_4: "Base building — 70% effort, technique focus, build run volume"
    weeks_5_8: "Intensity building — race pace intervals, full station practice"
    weeks_9_11: "Peak — race simulations, reduce volume, sharpen speed"
    week_12: "Taper — 50% volume, stay sharp, race day"
```

---

## Phase 5: Running & Cardio Programming

### Heart Rate Zones

| Zone | % Max HR | RPE | Purpose | Duration |
|------|---------|-----|---------|----------|
| Zone 1 | 50-60% | 2-3 | Recovery, warmup | Unlimited |
| Zone 2 | 60-70% | 4-5 | Aerobic base (80% of training) | 30-90+ min |
| Zone 3 | 70-80% | 6-7 | Tempo, threshold | 20-40 min |
| Zone 4 | 80-90% | 8-9 | VO2max intervals | 3-8 min intervals |
| Zone 5 | 90-100% | 10 | Sprint, anaerobic | 10-60 sec intervals |

**Max HR estimate:** 220 - age (rough) or 208 - (0.7 × age) (more accurate)

### 80/20 Rule

- 80% of running volume in Zone 1-2 (easy, conversational pace)
- 20% in Zone 3-5 (hard efforts)
- Violating this is the #1 mistake recreational runners make
- Easy runs should feel embarrassingly slow

### Running Progression Rules

1. **10% rule:** Increase weekly mileage by max 10%/week
2. **3-week build, 1-week back:** Build for 3 weeks, reduce 20-30% on 4th
3. **Long run:** Max 30% of weekly volume in one run
4. **Easy pace test:** Can hold full conversation? That's Zone 2.
5. **Speed work:** Only after 4+ weeks of consistent base building

### Conditioning Modalities for Hybrid Athletes

| Modality | Muscles | Cardio Benefit | Joint Impact | Hyrox Relevance |
|----------|---------|---------------|-------------|----------------|
| Running | Legs, core | High | High | Direct — 8km total |
| Rowing | Full body | High | Low | Direct — 1000m station |
| Ski Erg | Upper body, core | High | None | Direct — 1000m station |
| Assault Bike | Full body | Very high | None | Cross-training |
| Swimming | Full body | High | None | Active recovery |
| Cycling | Legs | Moderate-high | None | Zone 2 alternative |

---

## Phase 6: Recovery & Fatigue Management

### Recovery Priority Stack

| Priority | Method | Impact | Cost | Time |
|----------|--------|--------|------|------|
| 1 | Sleep 7-9 hours | ★★★★★ | Free | 7-9h |
| 2 | Protein 1.6-2.2g/kg | ★★★★★ | $$ | N/A |
| 3 | Hydration 35-45ml/kg | ★★★★ | Free | N/A |
| 4 | Deload weeks | ★★★★ | Free | 1 week/4-6 |
| 5 | Active recovery (Zone 1) | ★★★ | Free | 20-40 min |
| 6 | Mobility/stretching | ★★★ | Free | 10-15 min |
| 7 | Foam rolling | ★★ | $ | 10-15 min |
| 8 | Cold exposure | ★★ | $ | 2-5 min |
| 9 | Massage | ★★ | $$$ | 60 min |
| 10 | Compression garments | ★ | $$ | Wear post-session |

**Rules:**
- Never sacrifice #1-4 for #5-10
- Cold water immersion: useful for acute recovery between competitions, may blunt hypertrophy if used chronically post-strength training
- Foam rolling: pre-workout for mobility, post-workout for parasympathetic activation
- Sleep is the #1 performance enhancer. Period.

### Fatigue Monitoring

```yaml
daily_readiness:
  date: "YYYY-MM-DD"
  sleep_hours: 0
  sleep_quality: "1-5"  # 1=terrible, 5=great
  resting_hr: 0  # check first thing in morning
  hrv: 0  # if tracking
  muscle_soreness: "1-5"  # 1=none, 5=severe
  mood_energy: "1-5"  # 1=exhausted, 5=fired up
  motivation: "1-5"
  
  readiness_score: 0  # sum of quality+soreness(inverted)+mood+motivation = /20
  
  decision:
    # 16-20: Full intensity, push hard
    # 12-15: Normal training
    # 8-11: Reduce intensity or volume by 20%
    # 4-7: Active recovery or rest day
```

### Deload Protocol

| Component | Normal Week | Deload Week |
|-----------|------------|-------------|
| Volume (sets) | 100% | 50-60% |
| Intensity (weight) | Normal | Same or slightly reduce |
| Frequency | Normal | Same |
| Cardio volume | Normal | 50-70% |
| Duration | Normal | Shorter sessions |

**When to deload:**
- Planned: Every 4th week (intermediate), every 6-8th week (beginner)
- Reactive: 2+ sessions where RPE is higher than expected for same weight
- Sleep declining, motivation dropping, joint aches increasing
- Performance plateau for 2+ weeks despite adequate nutrition/sleep

---

## Phase 7: Nutrition for Training

### Calorie & Macro Targets

**Maintenance TDEE estimate:**
- Sedentary: BW(kg) × 26-28
- Lightly active (3x/week): BW(kg) × 30-32
- Active (5x/week): BW(kg) × 34-36
- Very active (6x+ hard training): BW(kg) × 38-42

**Goal-based adjustments:**
| Goal | Calorie Adjustment | Protein | Carbs | Fat |
|------|-------------------|---------|-------|-----|
| Muscle gain | +300-500 cal | 1.6-2.2 g/kg | 4-7 g/kg | 0.8-1.2 g/kg |
| Fat loss | -300-500 cal | 2.0-2.4 g/kg | 2-4 g/kg | 0.7-1.0 g/kg |
| Maintenance | 0 | 1.6-2.0 g/kg | 3-5 g/kg | 0.8-1.2 g/kg |
| Endurance heavy | +200-400 cal | 1.4-1.8 g/kg | 5-8 g/kg | 0.8-1.0 g/kg |
| Hybrid (Hyrox) | +0-300 cal | 1.8-2.2 g/kg | 4-6 g/kg | 0.8-1.0 g/kg |

### Pre/Intra/Post Workout Nutrition

| Timing | What | Why |
|--------|------|-----|
| 2-3h pre | Balanced meal (protein + carbs + fat) | Sustained energy |
| 30-60 min pre | Small snack (carbs + small protein) | Quick fuel, no GI distress |
| Intra (>60 min session) | 30-60g carbs/hour (sports drink, banana) | Maintain blood glucose |
| 0-2h post | Protein (30-40g) + carbs (0.8-1g/kg) | Recovery, glycogen replenishment |

### Supplements (Evidence-Based Only)

| Supplement | Dose | Evidence | When |
|-----------|------|----------|------|
| Creatine monohydrate | 3-5g daily | ★★★★★ | Any time, every day |
| Caffeine | 3-6 mg/kg | ★★★★★ | 30-60 min pre-workout |
| Protein powder | As needed to hit target | ★★★★ | Convenience — whole food first |
| Vitamin D | 1000-4000 IU daily | ★★★★ | If deficient (most people in UK) |
| Omega-3 (EPA/DHA) | 1-3g daily | ★★★ | Anti-inflammatory |
| Magnesium | 200-400mg daily | ★★★ | Sleep quality, recovery |
| Electrolytes | During long sessions | ★★★ | Sessions >60 min, hot weather |

**Don't waste money on:** BCAAs (if eating enough protein), testosterone boosters, fat burners, most pre-workout ingredients beyond caffeine.

---

## Phase 8: Mobility & Injury Prevention

### Daily Mobility Routine (10 min)

```
1. Cat-Cow — 10 reps (spine mobility)
2. World's Greatest Stretch — 5/side (hip flexor, T-spine, hamstring)
3. 90/90 Hip Switch — 10 reps (hip rotation)
4. Dead Hang — 30-60 sec (shoulder decompression)
5. Deep Squat Hold — 30-60 sec (ankle, hip mobility)
6. Band Pull-Aparts — 15 reps (shoulder health)
7. Couch Stretch — 30 sec/side (hip flexor)
```

### Pre-Workout Warmup Protocol

```
1. General: 5 min light cardio (jog, row, bike)
2. Dynamic stretches: leg swings, arm circles, hip circles (2 min)
3. Movement prep: bodyweight version of main lift (10 reps)
4. Ramping sets: 
   - Empty bar × 10
   - 40% × 8
   - 60% × 5
   - 75% × 3
   - 85% × 1
   - Working weight
```

### Common Issue Prevention

| Issue | Cause | Fix |
|-------|-------|-----|
| Low back pain | Weak core, hip tightness, poor bracing | McGill Big 3, hip flexor stretching, bracing drills |
| Shoulder impingement | Internal rotation dominance, weak rotator cuff | Face pulls, band external rotations, reduce overhead volume |
| Knee pain (anterior) | Quad dominance, weak VMO, poor ankle mobility | Terminal knee extensions, ankle dorsiflexion work, step-downs |
| Elbow tendinitis | Grip/wrist overuse, sudden volume increase | Wrist curls, eccentric work, reduce isolation curl volume |
| Hip shift in squat | Adductor/abductor imbalance, ankle restriction | Cossack squats, banded squats, heel elevation |

### When to See a Professional

- Sharp pain during or after exercise (not muscle soreness)
- Swelling that doesn't resolve in 48 hours
- Numbness or tingling
- Loss of range of motion lasting >2 weeks
- Pain that worsens with each session
- Any injury that changes your movement pattern

---

## Phase 9: Progress Tracking

### Workout Log YAML

```yaml
session:
  date: "YYYY-MM-DD"
  day: "Upper A"
  duration_min: 0
  location: ""
  readiness_score: 0  # from daily check
  
  exercises:
    - name: "Bench Press"
      warmup: "bar×10, 60×5, 80×3"
      working_sets:
        - { weight_kg: 95, reps: 5, rpe: 8 }
        - { weight_kg: 95, reps: 5, rpe: 8.5 }
        - { weight_kg: 95, reps: 4, rpe: 9 }
      notes: "Slight right shoulder tightness on last set"
    
    - name: "Weighted Pull-ups"
      working_sets:
        - { weight_kg: "+15", reps: 6, rpe: 8 }
        - { weight_kg: "+15", reps: 6, rpe: 8 }
        - { weight_kg: "+15", reps: 5, rpe: 9 }
  
  cardio:
    type: ""
    duration_min: 0
    distance_km: 0
    avg_hr: 0
    notes: ""
  
  session_notes: ""
  next_session_adjustments: ""
```

### Weekly Review Template

```yaml
weekly_review:
  week_of: "YYYY-MM-DD"
  sessions_completed: 0
  sessions_planned: 0
  
  strength_progress:
    squat: { weight: 0, reps: 0, trend: "↑/→/↓" }
    bench: { weight: 0, reps: 0, trend: "↑/→/↓" }
    deadlift: { weight: 0, reps: 0, trend: "↑/→/↓" }
  
  body_composition:
    weight_avg: 0  # 7-day average
    weight_trend: "↑/→/↓"
    waist_cm: 0  # weekly measurement
  
  cardio_volume:
    total_km: 0
    total_min: 0
    long_run_km: 0
  
  recovery_metrics:
    avg_sleep: 0
    avg_readiness: 0
    soreness_issues: ""
  
  wins: ""
  challenges: ""
  adjustments_for_next_week: ""
```

### Key Metrics to Track

| Metric | Frequency | Why |
|--------|-----------|-----|
| Working weights (all lifts) | Every session | Progressive overload verification |
| Body weight (morning, fasted) | Daily → weekly average | Body composition trending |
| Waist measurement | Weekly | Fat loss indicator (more reliable than scale) |
| Photos (front/side/back) | Every 4 weeks | Visual progress, mirrors lie |
| Run pace / distance | Every run | Cardio progression |
| Sleep hours + quality | Daily | Recovery capacity |
| RPE per set | Every session | Fatigue management |
| RHR / HRV | Daily (if tracking) | Readiness, overtraining early warning |

---

## Phase 10: Plateaus & Troubleshooting

### Plateau Decision Tree

```
Strength stalling?
├─ Eating enough? (surplus for gain, maintenance minimum)
│  └─ No → Fix nutrition first
├─ Sleeping 7+ hours?
│  └─ No → Fix sleep first
├─ Been training >4 weeks without deload?
│  └─ Yes → Deload, then reassess
├─ Same program >12 weeks?
│  └─ Yes → Change program (new stimulus)
├─ Volume too high? (approaching MRV)
│  └─ Yes → Reduce volume, increase intensity
├─ Volume too low? (at MEV)
│  └─ Yes → Add 1-2 sets/muscle/week
└─ All good? → Change rep range or exercise variation
```

### Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | No progressive overload (same weight every week) | Log every session, aim to beat last performance |
| 2 | Program hopping (new program every 2 weeks) | Stick to a program for minimum 8-12 weeks |
| 3 | Junk volume (30+ sets/muscle, half-effort) | Do fewer sets at higher effort (RPE 7-9) |
| 4 | Skipping legs | Follow balanced split — legs are 50%+ of your body |
| 5 | Never deloading | Schedule deloads, or take reactive deloads when signs appear |
| 6 | Ego lifting (too heavy, bad form) | Drop weight 20%, master form, then rebuild |
| 7 | Cardio killing gains | Separate cardio from lifting by 6+ hours, or do after lifting |
| 8 | Not eating enough protein | 1.6-2.2 g/kg — track for 2 weeks to calibrate |
| 9 | Ignoring sleep | 7-9 hours non-negotiable — it's when you grow |
| 10 | All intensity, no technique work | Record yourself, get form checks, invest in one coaching session |

---

## Phase 11: Body Composition Strategies

### Fat Loss Protocol

1. **Set deficit:** -300 to -500 cal/day (1% BW loss/week max)
2. **Protein HIGH:** 2.0-2.4 g/kg (muscle preservation is priority #1)
3. **Training:** Maintain intensity (heavy weights), reduce volume slightly if recovery drops
4. **Cardio:** Add 2-3 sessions of Zone 2 (walks, easy cycling), LISS > HIIT for sustainability
5. **Step target:** 8,000-12,000 steps/day (NEAT is the biggest calorie lever)
6. **Timeline:** Aim for 8-16 week cut, then 4+ weeks maintenance
7. **Refeed:** 1 day/week at maintenance with extra carbs if sub-15% BF
8. **When to stop:** Reaching target BF%, performance declining, diet fatigue >8/10

### Muscle Gain Protocol

1. **Set surplus:** +200-500 cal/day (0.5-1% BW gain/month for intermediates)
2. **Protein adequate:** 1.6-2.2 g/kg
3. **Training:** High volume focus (MAV range), progressive overload
4. **Cardio:** Minimal but maintain cardiovascular health (2x Zone 2, 20-30 min)
5. **Timeline:** Bulk for 12-20 weeks, then maintain or mini-cut
6. **When to stop:** BF% exceeding comfort (usually >18-20% men, >28-30% women), or at planned timeline

### Body Recomposition (Lose Fat + Gain Muscle)

**Who it works for:**
- Beginners (first 6-12 months)
- Detrained athletes returning
- Overweight beginners (higher BF% = more recomp potential)
- NOT effective for lean intermediates/advanced

**How:** Eat at maintenance, high protein (2.0+ g/kg), train hard with progressive overload. Trust the process — scale may not move but body composition changes.

---

## Phase 12: Competition & Race Prep

### Taper Protocol (Final 1-2 Weeks)

| Variable | 2 Weeks Out | 1 Week Out | 2 Days Out | Race Day |
|----------|-------------|------------|------------|----------|
| Volume | -30% | -50% | -70% | Race |
| Intensity | Maintain | 1-2 race pace efforts | Easy only | Race effort |
| Frequency | Normal | -1 session | Light movement | Race |
| Carbs | Normal | Slightly increase | Carb load (+2g/kg) | Race morning meal |
| Sleep | Priority | 8+ hours | 8+ hours (expect nerves) | Up early enough |

### Race Day Checklist

```yaml
race_day:
  morning:
    - Wake 3-4 hours before start
    - Familiar breakfast (tested in training)
    - Light caffeine if used in training
    - Kit check: shoes, watch, nutrition, number
    - Arrive 60-90 min before start
  
  warmup:
    - 10-15 min easy jog
    - Dynamic stretches
    - 2-3 race pace strides
    - Station-specific warmup (light ski erg pulls, bodyweight lunges)
  
  race_strategy:
    - Negative split: start conservative, build through middle, push final 2km
    - Station pacing: steady effort, don't redline early
    - Nutrition: sports drink/gel every 30-45 min
    - Mental cues: "relax, breathe, one station at a time"
  
  post_race:
    - Walk/easy movement for 10-15 min
    - Protein + carbs within 30 min
    - Rehydrate
    - Celebrate
    - Review within 24-48 hours while fresh
```

---

## Quality Rubric

Score any training program 0-100:

| Dimension | Weight | 0-25 | 50 | 75 | 100 |
|-----------|--------|------|-----|-----|------|
| Progressive overload | 20% | No tracking | Some logging | Consistent logging + progression | Planned periodized progression |
| Exercise selection | 15% | Random, unbalanced | Most patterns covered | All patterns, appropriate variations | Periodized exercise rotation |
| Volume/intensity | 15% | Way too much or little | Near MEV | MAV range, well managed | Individualized, auto-regulated |
| Recovery management | 15% | No rest days, poor sleep | Some structure | Planned deloads, good sleep | Full recovery protocol |
| Nutrition alignment | 15% | No awareness | Protein tracked | Full macro tracking | Periodized nutrition |
| Specificity to goal | 10% | Training doesn't match goal | Loosely aligned | Well-aligned | Competition-ready specificity |
| Adaptability | 5% | Rigid, no adjustment | Some flexibility | Reactive deloads, RPE-based | Auto-regulated, AI-assisted |
| Sustainability | 5% | Burnout trajectory | Manageable short-term | Sustainable long-term | Built for years, enjoyable |

---

## 10 Training Commandments

1. **Progressive overload or you're exercising, not training**
2. **Sleep is when you grow — protect it like your job depends on it**
3. **Protein is the only macro that MUST hit target daily**
4. **Consistency beats intensity — 80% effort for 52 weeks > 100% for 4**
5. **Track everything — what gets measured gets managed**
6. **Deload before you need to — proactive beats reactive**
7. **Ego is the enemy — perfect form at moderate weight beats ugly maxes**
8. **Specificity matters — train for YOUR goal, not someone else's program**
9. **Recovery is training — the workout is the stimulus, rest is the adaptation**
10. **Long game wins — think in years, not weeks**

---

## 10 Common Training Mistakes

| # | Mistake | Impact | Fix |
|---|---------|--------|-----|
| 1 | No program (winging it) | Zero progression | Pick a program and follow it 8-12 weeks |
| 2 | All cardio, no strength | Skinny-fat, injuries | Add 2-3 strength sessions/week minimum |
| 3 | Running too fast on easy days | Overtraining, injury | Use HR monitor — Zone 2 should feel easy |
| 4 | Skipping warmup | Injury risk, worse performance | 10 min: cardio + dynamic stretching + ramping sets |
| 5 | Only training what you like | Imbalances, injury | Program ALL movement patterns |
| 6 | Copying advanced athletes | Overtraining, frustration | Match program to YOUR training age |
| 7 | Relying on motivation | Inconsistency | Build habits, schedule sessions like meetings |
| 8 | Comparing to others | Discouragement | Track YOUR progress over months |
| 9 | Ignoring pain signals | Chronic injury | Sharp pain = stop, get assessed |
| 10 | Overcomplicating everything | Analysis paralysis | Simple program + consistency = 90% of results |

---

## Edge Cases

### Coming Back After Injury
- Start at 50% of previous weights
- Build back over 4-6 weeks
- Any exercise that causes pain gets swapped
- See physio for clearance before returning to sport

### Training Over 40
- Recovery takes longer — 3-4x/week often optimal
- Joint-friendly variations (trap bar deadlift, DB press)
- Warmup becomes non-negotiable
- Mobility work daily
- Prioritize eccentric control over heavy maxes

### Training in a Home Gym (Minimal Equipment)
- DB + bench + pull-up bar covers 90% of needs
- Resistance bands for rotator cuff and face pulls
- Adjustable DBs > fixed set (space + cost efficient)
- Priority buys: adjustable DBs → bench → pull-up bar → barbell + plates → rack

### Training + Shift Work
- Train after longest sleep block
- Keep schedule consistent on work days
- Caffeine cut-off 6h before sleep
- Meal prep is essential — no time for decisions

### Beginner Who's Afraid of the Gym
- Start with 2 weeks of bodyweight at home
- Go once to just walk around and do cardio
- Bring a program on your phone — purpose reduces anxiety
- Early morning or late evening = quieter
- Everyone started somewhere. Nobody is watching you.

---

## Natural Language Commands

- `/fitness-check` — Score any training program with the 8-signal health check
- `/design-program` — Build a periodized training program from athlete brief
- `/log-workout` — Record a training session with weights/reps/RPE
- `/weekly-review` — Generate weekly training summary and adjustments
- `/plateau-fix` — Diagnose and fix a strength or body composition plateau
- `/race-prep` — Create a taper and race day strategy
- `/nutrition-plan` — Calculate macros and create meal timing around training
- `/mobility-routine` — Generate a mobility routine for specific issues
- `/deload-check` — Assess whether a deload is needed
- `/exercise-swap` — Find an alternative exercise for equipment/injury constraints
- `/body-comp` — Set up a cut, bulk, or recomposition plan
- `/compare-programs` — Compare two programs for a specific athlete profile
