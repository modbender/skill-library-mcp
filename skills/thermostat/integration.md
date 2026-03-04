# Smart Home Integration — Agent Capabilities

## What Agent Can Do Per Platform

| Platform | Agent Capabilities |
|----------|-------------------|
| HomeKit | Set temp, change mode, query status via Siri/shortcuts |
| Alexa | Set temp, change mode, query status, set schedules via routines |
| Google Home | Set temp, change mode, query status, schedule via routines |
| Home Assistant | Full control: temps, modes, schedules, automations, sensor data |
| Matter | Cross-platform control, but advanced features need native app |

---

## Voice Command Patterns

**Teach user these work:**

| Action | Say This |
|--------|----------|
| Set exact temp | "Set thermostat to 70" |
| Relative adjust | "Turn up the heat" / "Make it warmer" |
| Change mode | "Set thermostat to cool" |
| Check status | "What's the thermostat set to?" |
| Activate scene | "Set home to away mode" |

**Gotcha:** "What's the temperature?" may return room sensor reading, not setpoint. Be specific about what user wants to know.

---

## Home Assistant Automations Agent Can Help Configure

**Auto-away when everyone leaves:**
```yaml
automation:
  trigger:
    - platform: state
      entity_id: group.family
      to: "not_home"
  action:
    - service: climate.set_temperature
      target:
        entity_id: climate.thermostat
      data:
        temperature: 62
```

**Pre-heat on approach:**
```yaml
automation:
  trigger:
    - platform: zone
      entity_id: device_tracker.phone
      zone: zone.home
      event: enter
  action:
    - service: climate.set_temperature
      data:
        temperature: 68
```

When user describes desired automation, help construct the YAML or guide through UI setup.

---

## Integration Troubleshooting

| Problem | Agent Diagnosis |
|---------|-----------------|
| "Alexa can't find my thermostat" | Re-discover devices, check skill is enabled and linked |
| "Voice command doesn't work" | Check exact phrasing, verify device name matches |
| "Shows wrong temperature" | Sensor vs setpoint confusion, or stale cache |
| "Automation didn't trigger" | Check condition logic, verify entities online |
| "Matter device won't pair" | Factory reset, ensure hub supports Matter, proximity during pairing |

---

## Multi-Zone Systems

**When user has multiple zones:**
- Each zone may appear as separate climate entity
- Or single entity with zone attributes (depends on integration)
- Help user understand which zone controls which rooms
- Schedule can differ per zone (sleep zone cooler at night)

**Common confusion:** "I set 70 but it shows 68" — Likely looking at different zone. Clarify which zone they're adjusting vs reading.
