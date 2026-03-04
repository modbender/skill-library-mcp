# Alexa Smart Home

## Device Setup

### Connection Methods

| Protocol | Requires Hub | Latency | Best For |
|----------|--------------|---------|----------|
| Wi-Fi | No | Low-Medium | Cameras, smart displays, standalone devices |
| Zigbee | Echo with hub or Zigbee hub | Low | Sensors, bulbs, switches (battery-friendly) |
| Z-Wave | Z-Wave hub | Low | Locks, thermostats, professional install |
| Matter | Thread border router or Wi-Fi | Very Low | Future-proof, local control |
| Bluetooth | No | Variable | Simple devices, audio |

### Adding Devices

1. **Enable skill for brand** (Alexa app → Skills → Search → Enable)
2. **Link account** (if required by manufacturer)
3. **Discover devices:** "Alexa, discover devices" or Devices → + → Add Device
4. **Assign to room** (critical for "turn off bedroom lights" to work)

**If device doesn't appear:**
- Check device is on same Wi-Fi network
- Factory reset device, re-add to manufacturer app first
- Disable/re-enable skill
- Check for device firmware updates

---

## Naming Best Practices

**Good names:**
- "Kitchen Light"
- "Living Room Fan"
- "Front Door Lock"
- "Bedroom TV"

**Bad names:**
- "Light 1" (ambiguous)
- "The Big One" (unclear device type)
- "Kitchen" alone (conflicts with room name)
- "LIFX A19 Color 1000 Bulb" (too long, hard to say)

**Rule:** Location + Device Type. Short, speakable, unique.

---

## Rooms & Groups

### Rooms
Assign devices to rooms for natural commands:
- "Turn off the bedroom" (all devices in bedroom)
- "What's the temperature in the kitchen?" (thermostat in kitchen)

### Device Groups
Group similar devices across rooms:
- "Downstairs Lights" → all lights on first floor
- "All Speakers" → multi-room audio

### Scenes
Preset states for multiple devices:
- "Movie Time" → dim lights, turn on TV, close blinds
- "Good Night" → lock doors, lights off, thermostat to 68°

---

## Routines

### Trigger Types

| Trigger | Example |
|---------|---------|
| Voice | "Alexa, good morning" |
| Schedule | Every weekday at 7:00 AM |
| Device state | Front door lock unlocks |
| Location (geofence) | Arrive home / Leave home |
| Alarm dismissed | Morning alarm turned off |
| Echo Button | Physical button press |
| Guard | Sound detected (glass break, smoke alarm) |

### Actions

- Smart home: control devices, scenes
- Announcements: speak on specific or all Echo devices
- Messaging: send notifications, make calls
- Music/News: play specific content
- Skills: trigger skill actions
- Wait: pause between actions
- Custom responses: Alexa says specific phrase

### Routine Tips

**Make it reliable:**
- Use unique trigger phrases (not similar to built-in commands)
- Test each step individually before combining
- Add waits between actions if devices are slow
- Check routine history for failures

**Power user patterns:**
- "Leaving home" routine: lock doors, arm Guard, turn off all lights, adjust thermostat
- "Cooking" routine: set timer, play music, turn on kitchen lights to 100%
- "Guest mode" routine: disable sensitive routines, change Wi-Fi password

---

## Multi-Room Audio

**Setup:**
1. Create speaker group in Alexa app
2. Add Echo devices or compatible speakers
3. Name the group ("Everywhere", "Downstairs")

**Commands:**
- "Play jazz on the downstairs group"
- "Move music to kitchen" (transfer playback)
- "Play [music] everywhere"

**Limitations:**
- All speakers must be on same account
- Some non-Echo speakers have lag
- Different music services have different multi-room support

---

## Troubleshooting

### Device Issues

| Symptom | Check |
|---------|-------|
| "Device not responding" | Wi-Fi connection, device power, manufacturer app |
| Slow response | Wi-Fi congestion, move closer to router |
| Commands misheard | Check utterance history in Alexa app |
| Device works in app but not voice | Room assignment, device name pronunciation |
| Zigbee device drops | Move closer to hub, check for interference |

### Routine Issues

| Symptom | Check |
|---------|-------|
| Routine doesn't trigger | Trigger phrase conflict, check routine history |
| Partial execution | Device offline during routine |
| Location trigger fails | Phone location permissions, Alexa app battery optimization |
| Scheduled routine missed | Device offline, time zone settings |

### Reset Procedures

**Echo device:**
1. Press and hold Action button (dot) for 25 seconds
2. Wait for orange ring → device in setup mode

**Re-register all devices:**
1. Disable and remove all smart home skills
2. Delete all devices from Alexa app
3. Factory reset devices if needed
4. Re-add manufacturer apps, re-enable skills
5. Discover devices fresh

---

## Privacy & Security

**Voice recording controls:**
- Review voice history: Alexa app → Privacy → Review Voice History
- Auto-delete: Set to delete after 3 or 18 months
- "Alexa, delete what I just said"
- "Alexa, delete everything I said today"

**Cameras and Ring:**
- Privacy mode to disable camera
- Motion zones to limit recording areas
- Shared users vs guests (different permission levels)

**Guest Connect:**
- Visitors use their own Amazon account on your Echo
- Their requests billed to their account
- Your smart home still controlled

**Drop In:**
- Enable only for trusted contacts
- Set to household only or specific contacts
- Check privacy settings per device
