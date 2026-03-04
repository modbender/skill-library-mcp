---
name: Thermostat
description: Adjust temperatures, diagnose comfort issues, calculate energy savings, and automate schedules through voice commands or smart home integration.
---

## What the Agent Can Do

| User Request | Agent Action |
|--------------|--------------|
| "Make it warmer/cooler" | Adjust setpoint ±2-3°F or to specific temp |
| "Why is my bedroom cold?" | Diagnose: sensor location, vent issues, zone problems |
| "Set up a schedule" | Gather wake/leave/return/sleep times → configure |
| "Am I wasting money?" | Calculate setback savings, identify inefficiencies |
| "I'm going on vacation" | Set freeze protection (55°F) or vacancy mode |
| "Something's wrong with my heat" | Troubleshoot: cycles, error codes, aux heat issues |

---

## Before Adjusting Temperature

**Gather context:**
- Current temp and setpoint
- Heating or cooling mode?
- Smart thermostat or basic?
- Any specific room complaints?

**Smart thermostats:** Adjust via voice, app command, or API integration.
**Basic thermostats:** Guide user to physical adjustment, suggest smart plug workarounds if relevant.

---

## Diagnosing Comfort Problems

When user says "it's too hot/cold":

1. **Check location mismatch** — Thermostat in hallway but complaint is bedroom? Sensor measures wrong place. Solution: remote sensors or door management.

2. **Check system behavior** — Running constantly? Short cycling (<5 min)? Not turning on? Each has different diagnosis path. See `troubleshooting.md`.

3. **Check settings** — Wrong mode? Hold preventing schedule? Eco mode active unexpectedly?

---

## Energy Calculations

When user asks about savings:

**Setback rule of thumb:** 1°F setback for 8 hours = ~1% savings.

| Scenario | Estimated savings |
|----------|-------------------|
| 10°F night setback (8h) | 5-15% |
| 10°F work setback (8h) | 5-15% |
| Both combined | 10-25% |

**Heat pump exception:** Deep setbacks may trigger expensive aux heat. Recommend 3-5°F max for heat pumps.

**Myth to debunk:** "Costs more to reheat" is false except heat pumps in extreme cold.

---

## Vacation/Away Configuration

**Short away (hours):** Set 62°F heat / 82°F cool.

**Extended vacation:**
- Minimum 55°F (pipe freeze protection)
- Maximum 85°F (humidity/mold prevention)
- Enable leak sensor alerts if available

**Remind user:** Set return date or use geofencing to avoid coming home to extreme temps.

---

## Load Detailed Reference

| Situation | Reference |
|-----------|-----------|
| Mode explanations, holds, fan settings | `basics.md` |
| System not responding, error codes, HVAC issues | `troubleshooting.md` |
| Cost calculations, efficiency tips, renter workarounds | `efficiency.md` |
| HomeKit, Alexa, Google, Home Assistant, Matter | `integration.md` |
| Vacation settings, freeze protection, humidity | `away.md` |
