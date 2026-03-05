# Bluetooth Use Cases

## Audio Devices

### Switching Between Devices
User: "Switch to my headphones"
```
1. Check ~/bluetooth/profiles/ for device with type: audio/headphones
2. If current audio device connected → disconnect gracefully
3. Connect to headphones using saved connection method
4. Verify audio routing changed (play test sound if uncertain)
5. Confirm to user: "Switched to Sony WH-1000XM5"
```

### Multi-Device Management
User: "List my audio devices"
```
1. Read all profiles with type: audio/*
2. For each, check connection status
3. Present: name, type, status, battery if available
```

### Audio Quality Settings
User: "Enable high quality mode"
```
1. Check if device supports aptX/LDAC/AAC
2. Adjust codec priority in system settings
3. May require reconnection to apply
4. Verify with: "Codec now: aptX HD"
```

---

## Smart Home

### Scene Execution
User: "Goodnight mode"
```
1. Lookup devices tagged "bedroom" or "goodnight-scene"
2. For each:
   - Lights → off or dim to 5%
   - Locks → verify locked
   - Thermostat → night temp
3. Execute in parallel where possible
4. Report failures: "Bedroom lamp didn't respond, retrying..."
```

### Device Discovery
User: "Find new devices"
```
1. Confirm: "Scanning for 30 seconds. Make sure devices are in pairing mode."
2. Scan with appropriate tool
3. Filter out already-profiled devices
4. Present new devices: "Found 2 new: 'LED Strip' and 'SmartPlug'"
5. Offer to profile each
```

### Troubleshooting
User: "The kitchen light isn't responding"
```
1. Load profile for kitchen light
2. Check if in range (recent RSSI readings)
3. Attempt reconnection
4. If fails: suggest power cycle, re-pair
5. Update profile with issue and resolution
```

---

## Fitness Wearables

### Data Extraction
User: "Get my workout from the watch"
```
1. Connect to fitness device
2. Read workout data from relevant GATT characteristics
3. Parse into standard format (FIT/TCX preferred)
4. Save to designated location
5. Offer to sync to Strava/Garmin Connect
```

### Live Metrics
User: "Show my heart rate"
```
1. Connect to HR sensor
2. Subscribe to heart rate characteristic
3. Stream readings: "Current: 72 bpm"
4. Maintain connection until user says stop
5. Log session for history
```

### Multi-Device Sync
User: "Sync everything"
```
1. List all fitness devices in profiles
2. Connect to each sequentially
3. Extract new data from each
4. Consolidate into unified health log
5. Push to configured apps (Health, Strava, etc.)
```

---

## Development/Maker

### Device Analysis
User: "What can this device do?"
```
1. Connect to device
2. Enumerate all GATT services
3. For each service:
   - Identify by UUID (check standard UUIDs first)
   - List characteristics with properties (read/write/notify)
4. Present structured view:
   "Service: Heart Rate (0x180D)
    - Measurement (notify): reads HR data
    - Body Sensor Location (read): where sensor is worn"
```

### Protocol Reverse Engineering
User: "Capture traffic from this device"
```
1. Start btmon/PacketLogger
2. Perform device interactions
3. Capture HCI/GATT traffic
4. Help decode: "Looks like characteristic 0x2A19 is battery level"
5. Save capture for analysis
```

### Creating Device Profile
User: "Figure out how to control this LED strip"
```
1. Connect and enumerate services
2. Find likely control characteristic (writeable, in custom service)
3. Experiment with values: 0x00, 0x01, 0xFF
4. Correlate observed behavior
5. Document in profile: "Write 0x01 to char X turns on"
```

---

## Common Patterns

### Connection Template
```
1. Load profile (or discover if new)
2. Check device in range
3. Connect with timeout
4. Verify connection (read a known characteristic)
5. Execute requested operation
6. Verify result
7. Update profile with outcome
8. Disconnect gracefully (or maintain per profile settings)
```

### Error Recovery
```
1. First failure: retry immediately
2. Second failure: wait 2 seconds, retry
3. Third failure: alert user, offer diagnostics
4. Log all attempts for pattern analysis
```

### Batch Operations
```
When multiple devices need commands:
1. Sort by priority (user-facing first)
2. Execute in parallel where independent
3. Collect results
4. Report summary: "3/4 devices responded, retrying kitchen light..."
```
