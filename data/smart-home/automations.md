# Smart Home Automation Patterns

## Core Patterns

### Presence-Based
| Trigger | Action |
|---------|--------|
| Everyone leaves | Lights off, thermostat to away mode, arm security |
| First person arrives | Lights on (if dark), thermostat to comfort, disarm security |
| Last person to bed | Everything off except bedroom, doors locked |

**Implementation:** Geofencing (phone location) or motion sensor timeout (no motion for 30 min = away)

### Time-Based
| Trigger | Action |
|---------|--------|
| Sunrise - 30 min | Bedroom lights gradually brighten |
| Sunset | Outdoor lights on, living room lights on |
| 10 PM | Porch lights dim, interior prepares for night |
| 6 AM weekdays | Coffee maker on (if plugged into smart plug) |

### Event-Based
| Trigger | Action |
|---------|--------|
| Front door unlocks | Entry lights on |
| Door open > 5 min | Notification + auto-close if motorized |
| Water leak detected | Shut off main valve (if smart), immediate notification |
| Smoke detector | All lights on 100%, unlock doors |

---

## Room-by-Room Templates

### Bedroom
- Wake-up: Lights gradually increase over 15-30 min
- Bedtime: "Good night" scene dims all, sets alarm, locks doors
- Motion at night: Dim path lighting only (10-20%)

### Kitchen
- Morning: Counter lights on, coffee maker (if smart plug)
- Cooking mode: Hood fan auto-on with stove sensor
- Evening: Under-cabinet lights on at sunset

### Living Room
- Movie mode: Dim lights, TV on, blinds close
- Evening mode: Ambient lighting at sunset
- Away: Random light patterns to simulate occupancy

### Bathroom
- Motion: Lights on (dim at night, bright during day)
- Humidity spike: Exhaust fan on for 15 min after
- No motion 5 min: Lights off

### Garage
- Door opens: Light on
- Door open > 10 min: Notification
- Car arrives (door opens + motion): Welcome lights inside

---

## Automation Mistakes to Avoid

| Mistake | Why it fails |
|---------|--------------|
| Lights off on no motion (short timeout) | Walking into dark room repeatedly |
| Thermostat away mode on phone leaving | Single person home, phone dies |
| Auto-lock too aggressive | Locked out while taking trash out |
| Too many notifications | Alert fatigue, start ignoring |
| Complex scenes no one remembers | Family can't operate house |

---

## Robust Automation Checklist

- [ ] Tested with multiple people home
- [ ] Works when internet is down (local execution)
- [ ] Has manual override that's obvious
- [ ] Notifications only for actionable events
- [ ] Spouse/family can explain how it works
- [ ] Timeout values tested over a week
