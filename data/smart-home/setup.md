# Smart Home Setup Guide

## Choosing Your Ecosystem

### By existing devices
- **iPhone + Apple TV/HomePod** → Start with HomeKit
- **Android + Google speakers** → Start with Google Home
- **Echo devices** → Start with Alexa
- **No preference / want flexibility** → Start with Home Assistant or Hubitat

### By technical comfort
| Level | Recommendation |
|-------|----------------|
| Non-technical | Apple HomeKit (simplest), Google Home, or Alexa |
| Some comfort | SmartThings, Hubitat |
| Technical | Home Assistant (most powerful, steepest learning curve) |

---

## Protocol Decision

### Go with Matter/Thread if:
- Starting fresh in 2024+
- Want maximum future compatibility
- Buying new devices anyway

### Go with Zigbee if:
- Need battery-powered sensors
- Want mesh reliability
- Budget-conscious (many affordable options)

### Go with Z-Wave if:
- Need maximum range through walls
- Critical devices (locks, garage)
- Live in large home

### Go with WiFi for:
- Cameras (need bandwidth)
- Devices that don't need mesh
- Simple single-device additions

---

## Hub Selection

### No hub needed
- Under 10 devices
- Single ecosystem (all Hue, all Ring, etc.)
- Basic scenes only

### Hub recommended
| Hub | Best for | Complexity |
|-----|----------|------------|
| Apple TV/HomePod | HomeKit devices, iPhone users | Low |
| Echo Plus/Show | Alexa-first, Zigbee devices | Low |
| SmartThings | Mixed ecosystems, Matter | Medium |
| Hubitat | Local control, Z-Wave/Zigbee | Medium |
| Home Assistant | Maximum flexibility, tinkerers | High |

---

## First Purchases by Budget

### Under €100 (Starter)
1. Smart plug (2-pack) — automate lamps, fans
2. Smart bulb (2-pack) — bedroom, living room
3. Motion sensor — hallway automation

### €100-300 (Essentials)
1. Smart hub (if needed)
2. Smart thermostat — biggest energy savings
3. Smart lock or video doorbell — pick one
4. Motion/contact sensors (3-4)
5. Smart bulbs for main rooms

### €300-800 (Complete)
All of above, plus:
- Full home lighting (switches or bulbs)
- Video doorbell AND smart lock
- Leak sensors (kitchen, bathroom, laundry)
- Smart blinds (1-2 rooms)
- Outdoor lighting

---

## Getting Started Checklist

- [ ] Inventory existing devices and accounts
- [ ] Choose primary ecosystem (HomeKit/Google/Alexa/HA)
- [ ] Set up IoT VLAN on router (see `security.md`)
- [ ] Install hub if needed
- [ ] Add first 3 devices
- [ ] Create first automation (e.g., lights at sunset)
- [ ] Live with it for 2 weeks before adding more
