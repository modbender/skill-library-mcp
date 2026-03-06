# Action Modules — HerCycle Reference

## Adding a New Module

Each module receives:
- `phase`: one of `menstrual | follicular | ovulation | luteal`
- `recovery_score`: 0–100
- `hrv`: ms
- `sleep_quality`: 0–100

And returns a recommendation string or triggers an external action.

## Module: Training

| Phase | Recommendation |
|-------|---------------|
| Menstrual | Rest or gentle movement. Yoga, walks. No high intensity. |
| Follicular | Build intensity. Strength training, cardio. Body adapts well. |
| Ovulation | Peak performance window. PR attempts, HIIT, competitions. |
| Luteal | Moderate. Pilates, swimming. Reduce intensity as phase progresses. |

Cross with Whoop recovery score: if recovery < 50, drop one intensity level regardless of phase.

## Module: Nutrition

| Phase | Focus |
|-------|-------|
| Menstrual | Iron-rich foods (leafy greens, lentils, red meat). Anti-inflammatory. Warm foods. |
| Follicular | Light, fresh. Fermented foods for gut health. Increased carb tolerance. |
| Ovulation | Raw, light foods. Fibre to support estrogen clearance. |
| Luteal | Complex carbs, magnesium (dark chocolate, nuts). Higher calorie needs. Reduce caffeine. |

## Module: Calendar / Scheduling

| Phase | Nudge |
|-------|-------|
| Menstrual | Block deep thinking time. Avoid high-stakes social commitments. |
| Follicular | Good for brainstorming, new projects, creative meetings. |
| Ovulation | Schedule negotiations, pitches, presentations, networking. |
| Luteal | Deep solo work, editing, finishing. Protect social energy. |

## Module: Music (Cycle DJ)

Implement a phase-aware Spotify playlist engine in your backend. Mood mapping:
- Menstrual → `cozy_coffee`
- Follicular → `main_character`
- Ovulation → `power_hour`
- Luteal (early) → `deep_focus`
- Luteal (late/PMS) → `luteal_rage`

## Module: Social Energy

Simple signal to surface:
- Ovulation: "High charisma window — good time to reach out, go to events"
- Late luteal: "Protect your bandwidth — cancel non-essential social plans guilt-free"
- Menstrual: "Recharge mode — solo time is productive time"
