---
name: war-intel-monitor
description: Real-time war intelligence monitoring and emergency alert system for conflict zones. Use when user needs to track military conflicts, receive emergency alerts, monitor evacuation options, or assess safety risks during wartime situations. Supports customizable location-based threat assessment with distance calculations to military targets.
---

# War Intelligence Monitor

Real-time conflict monitoring system with location-based threat assessment.

## Setup

Before using, configure user profile in `config.json`:

```json
{
  "user_location": {
    "name": "Your Location Name",
    "coordinates": [latitude, longitude],
    "shelter_primary": "Nearest shelter location",
    "shelter_secondary": "Backup shelter location"
  },
  "evacuation_target": "Target city/country",
  "known_targets": [
    {"name": "Military Base A", "distance_km": 20, "type": "military"},
    {"name": "Airport", "distance_km": 15, "type": "infrastructure"},
    {"name": "Port", "distance_km": 25, "type": "infrastructure"}
  ],
  "emergency_contacts": {
    "police": "emergency number",
    "ambulance": "emergency number",
    "embassy": "embassy number"
  }
}
```

## Monitoring Workflow

### 1. Set Up Cron Jobs

Create two monitoring jobs:

**Urgent Monitoring (every 30 min)**
```
Execute war intel monitoring:
1. Search latest news: [conflict keywords]
2. Check for red alert keywords (airspace closed, missile launch, air raid, explosion)
3. If emergency detected, send alert immediately
4. Include distance from user location for each target mentioned

Alert format:
🚨 [RED ALERT] {event}
📍 Distance from you: ~{X}km
⚡ Immediate actions: {actions}
📊 Next 24-72h forecast: {prediction}
```

**Daily Briefing (3x daily)**
```
Generate daily briefing:
1. Search past 6 hours news
2. Check airspace status
3. Query flight prices and availability to evacuation target
4. Provide risk assessment and recommendations
```

### 2. Alert Levels

| Level | Trigger | Response |
|-------|---------|----------|
| 🔴 Red | Airspace closed, missile launch, direct attack | Immediate shelter, action instructions |
| 🟡 Yellow | Military buildup, diplomatic breakdown, oil spike >10% | Prepare, monitor signals |
| 🟢 Green | Routine monitoring | Daily briefing |

### 3. Alert Template

```
🚨 [ALERT LEVEL] {Event Type}

📍 Location: {target_name}
📏 Distance from you: ~{distance}km

⚡ Immediate Actions:
1. {action_1}
2. {action_2}
3. {action_3}

📊 Situation Assessment:
{brief_analysis}

🔗 Source: {source}
```

### 4. Briefing Template

```
📋 Daily Briefing - {date}

🎯 Situation Summary:
{overview}

📍 Recent Incidents (with distances):
| Target | Distance | Status |
|--------|----------|--------|
| {name} | {km}km | {status} |

✈️ Evacuation Options:
- Flight availability: {status}
- Prices: {price_range}
- Recommendation: {recommendation}

🛡️ Risk Assessment: {level}
{reasoning}
```

## Safety Guidelines

### Shelter Priorities
1. Underground parking / basement
2. Bathroom (no windows, reinforced walls)
3. Interior corridor (away from exterior walls)
4. Lowest floor, interior room

### Go Bag Checklist
- [ ] Passport + copies
- [ ] Cash (local + USD)
- [ ] Phone + charger + power bank
- [ ] Water bottles
- [ ] High-calorie snacks
- [ ] Work gloves (for debris)
- [ ] Flashlight
- [ ] First aid basics
- [ ] Important documents

### During Attack
1. Move away from windows immediately
2. Drop to floor if explosion heard
3. Cover head and neck
4. Wait 10-15 seconds before moving
5. Check for injuries, then assess surroundings

## Information Sources

### Official Sources (Priority)
- National emergency management agency
- Ministry of Defense statements
- Embassy alerts
- Civil aviation authority

### OSINT Sources
- FlightRadar24 (airspace status)
- MarineTraffic (shipping lanes)
- Verified news agencies
- Official government social media

### Financial Indicators
- Oil prices (Brent/WTI)
- Currency fluctuations
- Prediction markets (Polymarket)
- Flight price trends

## Customization

Edit `config.json` to customize:
- Your location and coordinates
- Known military/infrastructure targets with distances
- Evacuation destination
- Emergency contacts
- Alert keywords in local language
