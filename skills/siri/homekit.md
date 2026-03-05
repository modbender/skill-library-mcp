# Siri HomeKit Control

## Device Naming Best Practices

**Format:** Location + Function
- ✅ "Kitchen Light", "Bedroom Fan", "Front Door Lock"
- ❌ "Light 1", "Lamp", "Smart Bulb #3"

**Naming Rules:**
- No punctuation or special characters
- Avoid numbers unless meaningful ("Floor 2 Hallway")
- Keep names short (2-3 words ideal)
- Make names phonetically distinct
- Test by saying the command before committing

---

## Room & Zone Setup

**Rooms:**
- Group devices by physical location
- HomePod knows which room it's in (responds to "turn off the lights")
- Create in Home app → + → Add Room

**Zones:**
- Group multiple rooms: "Downstairs", "Upstairs", "Outdoors"
- Home app → Room Settings → Add to Zone
- Commands: "Turn off downstairs" / "Lock all outdoor doors"

**Multi-Home:**
- "Set the [Home Name] to [temperature]"
- "Turn on lights at the beach house"
- Each home needs its own hub

---

## Scene Commands

**Built-in Suggestions:**
- "Good Morning" / "Good Night"
- "I'm Leaving" / "I'm Home"
- "Movie Time"

**Creating Scenes:**
Home app → + → Add Scene → Custom
Name it for voice activation: "Start cooking", "Party mode"

**Voice Activation:**
- "Hey Siri, [scene name]"
- "Set the scene to [name]"
- "Activate [name]"

---

## Automation Triggers

**Time-Based:**
- "Turn on porch light at sunset"
- "Lock doors at 10 PM every night"
- (Requires Home app automation setup, not voice-creatable)

**Location-Based:**
- "When I leave home, turn off all lights"
- Uses phone location, requires permission

**Accessory-Based:**
- "When front door unlocks, turn on hallway light"
- Sensor triggers: motion, contact, temperature

---

## Status Queries

- "Are the lights on?"
- "Is the front door locked?"
- "What's the temperature in the living room?"
- "Is anyone home?" (requires location sharing with Home)
- "Show me [camera name]"

---

## Security Accessories

**Lock Behavior:**
- Unlocking requires device unlock or voice verification
- "Hey Siri, unlock the front door" → may require Face ID/Touch ID

**Garage Doors:**
- Same security behavior as locks
- "Open the garage" may require authentication

**Cameras:**
- "Show me [camera name]" displays on device/HomePod with screen
- HomeKit Secure Video for recording

---

## Home Hub Requirements

**For Remote Access:**
- HomePod (any model)
- Apple TV (4th gen or later)
- iPad (left at home, signed in)

**Hub Status:**
Home app → Home Settings → Home Hubs
Should show "Connected" for remote commands to work

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No Response" | Check device in Home app, verify hub is connected, reboot device |
| Wrong light responds | Rename with more specific location |
| Scene not activating | Check scene name pronunciation, rename if needed |
| Remote control not working | Verify home hub status in Home app settings |
| Automation didn't run | Check automation conditions in Home app |
| New device not appearing | Re-add from manufacturer app, then link to HomeKit |

---

## Siri vs Home App

**Use Siri for:**
- Quick commands ("Turn off kitchen")
- Scene activation
- Status checks

**Use Home app for:**
- Creating automations
- Device setup and renaming
- Troubleshooting offline devices
- Viewing camera feeds
- Managing home members
