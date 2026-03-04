# Device Profile Management

## Profile Structure

Each device gets a file in `~/bluetooth/profiles/`:

```markdown
# Device: Living Room Speaker

## Identity
- **MAC:** AA:BB:CC:DD:EE:FF
- **Name:** JBL Flip 5
- **Type:** audio/speaker
- **First seen:** 2024-01-15
- **Last connected:** 2024-02-10

## Connection
- **Protocol:** A2DP (Classic Bluetooth)
- **Pairing:** PIN required (0000)
- **Auto-connect:** yes
- **RSSI typical:** -55 to -70 dBm

## Capabilities
- Play/pause via AVRCP
- Volume control (0-127)
- Battery level readable
- No microphone

## Commands That Work
- `blueutil --connect AA:BB:CC` → connects in ~2s
- AVRCP play: reliable
- AVRCP next/prev: reliable

## Known Issues
- Disconnects if idle >10 min
- Needs re-pair after firmware update
- Volume sync with macOS is laggy

## Notes
- User prefers this for kitchen music
- Connected to Mac mini primarily
```

---

## Creating New Profiles

When encountering unknown device:

1. **Discover basics**
   ```bash
   # Linux
   bluetoothctl info XX:XX:XX

   # macOS
   blueutil --info XX:XX:XX
   ```

2. **Identify device type**
   - Check advertised services (A2DP, HID, GATT)
   - Note manufacturer from OUI lookup
   - Ask user what the device is

3. **Test connection**
   - Attempt pair, note PIN requirements
   - Attempt connect, note time and stability
   - Try basic commands for device type

4. **Document findings**
   - Create profile file with observed behavior
   - Mark confidence level (new device = low confidence)

---

## Profile Learning (Sponge System)

### After Each Interaction

Update the profile with:
- Did command succeed? → add to "Commands That Work"
- Did command fail? → add to "Known Issues"
- New capability discovered? → add to "Capabilities"
- Timing observations? → update connection notes

### Confidence Scoring

```
new device:        ★☆☆☆☆
basic commands ok: ★★☆☆☆
stable connection: ★★★☆☆
full capabilities: ★★★★☆
battle-tested:     ★★★★★
```

### Profile Aging

If device not seen in 90 days:
- Mark as "possibly stale"
- Don't auto-delete (user might travel with device)
- On next connection, re-verify profile

---

## Device Type Templates

### Audio (Speaker/Headphones)
```
Capabilities: play, pause, next, prev, volume, battery
Protocol: A2DP + AVRCP
Test: play audio, verify sound, check volume control
```

### Smart Home (Lights/Locks)
```
Capabilities: depends on GATT services
Protocol: BLE with custom characteristics
Test: toggle state, verify change, note timing
```

### Fitness (Wearables)
```
Capabilities: heart rate, steps, battery, sync
Protocol: BLE GATT
Test: read live values, compare to device display
```

### Input (Keyboards/Mice)
```
Capabilities: HID reports
Protocol: HID over GATT or Classic
Test: press keys, verify input registered
```

---

## Searching Profiles

```bash
# Find all audio devices
grep -l "Type: audio" ~/bluetooth/profiles/*.md

# Find devices with connection issues
grep -l "Known Issues" ~/bluetooth/profiles/*.md

# Find recently used
ls -lt ~/bluetooth/profiles/ | head -10
```
