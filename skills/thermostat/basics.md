# Thermostat Basics — Reference for Agent

## Modes (When User Asks "What Mode Should I Use?")

| Mode | Use When | Agent Recommendation |
|------|----------|---------------------|
| Heat | Winter, heating only needed | Default for cold months |
| Cool | Summer, cooling only needed | Default for warm months |
| Auto | Shoulder seasons, variable temps | When daily high/low span >15°F |
| Off | Mild weather, windows open | When outdoor temp 65-75°F |

**Auto mode requires deadband** — Minimum 2-3°F gap between heat and cool setpoints. If user tries heat:72 cool:73, explain this won't work.

---

## Holds — Explaining to Users

| Hold Type | What Happens | When to Recommend |
|-----------|--------------|-------------------|
| Permanent | Stays until manually changed | "Keep it 70 until I say otherwise" |
| Temporary | Reverts at next schedule period | "Just for this afternoon" |
| Until time | Holds until specific time | "Until I get home at 6pm" |

**Common user confusion:** Manual adjustment may create permanent hold when they wanted temporary. If user complains schedule isn't working, check hold status first.

---

## Fan Settings — When Asked

| Setting | Recommend When |
|---------|----------------|
| Auto | Default, most efficient |
| Circulate | Hot/cold spots between rooms, multi-story homes |
| Always On | Rarely — only if air quality concerns |

**Circulation mode** (Nest, Ecobee): Runs fan 15-20 min/hour without heating/cooling. Explain this uses ~$5-10/month extra electricity but evens temperatures.

---

## Remote Sensors — Setup Guidance

When user has or is considering remote sensors:

**Placement recommendations:**
- 4-5 feet height (breathing level)
- Away from vents, windows, exterior doors
- In rooms they actually occupy (bedroom for sleep, office for work)

**Priority/weighting:** Most thermostats let user prioritize rooms by time of day. Ask: "Which room matters most at night? During the day?"

---

## Schedule Setup — Information to Gather

When user wants a schedule, collect:

1. **Wake time** — When do you get up? What temp feels comfortable?
2. **Leave time** — When do you leave? (Can setback 8-10°F)
3. **Return time** — When are you usually home? (Pre-heat 30-60 min before)
4. **Sleep time** — When do you go to bed? (Most people sleep better 65-68°F)

**Pre-conditioning note:** Explain that "7am = 68°F" means REACH 68 by 7am, so system starts 30-60 min earlier depending on house and outdoor temp.
