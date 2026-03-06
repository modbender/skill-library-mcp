# Bluetooth Security Rules

## Mandatory Rules

### 1. Device Whitelisting
- **Only interact with pre-authorized devices**
- First connection requires explicit user confirmation
- Store approved devices in `~/bluetooth/profiles/`
- Unknown devices go to `~/bluetooth/pending.md` for review

### 2. Connection Logging
- Log every connection attempt with timestamp
- Log every command sent and result received
- Log disconnections (graceful and unexpected)
- Retain logs for troubleshooting and audit

### 3. Pairing Confirmation
- **Never auto-accept pairing requests**
- Display pairing code to user for verification
- Require explicit "yes" before completing pair
- Document PIN/passkey in profile (if static)

### 4. Timeout Enforcement
- Connection attempts: 15 second timeout
- Command execution: 5 second timeout
- Idle connections: disconnect after 5 minutes
- Scanning: stop after 30 seconds unless user extends

---

## NEVER Do These

| Action | Why Dangerous |
|--------|---------------|
| Auto-connect to new devices | Could be attacker's device with spoofed name |
| Continuous scanning | Reveals your presence, drains battery, attracts attacks |
| Store pairing keys in plain text | Keys allow reconnection without consent |
| Send credentials over BLE | BLE encryption is weak, often absent |
| Trust device name | Names are trivially spoofed |
| Ignore weak signal devices | Except: -80dBm+ is suspicious (distant attacker) |
| Expose MAC addresses externally | MAC = persistent identifier = privacy leak |

---

## Known Vulnerabilities

### BLE Just Works Pairing
- Zero authentication in many devices
- MITM trivial during pairing
- **Mitigation:** Verify device physically when pairing

### MAC Address Tracking
- Fixed MACs enable location tracking
- Some devices rotate MACs (iPhones)
- **Mitigation:** Never log MACs to external services

### Replay Attacks
- Captured commands can be replayed
- Devices without timestamps are vulnerable
- **Mitigation:** Use sequence numbers if supported

### BlueBorne-style Attacks
- Stack vulnerabilities in OS Bluetooth implementation
- **Mitigation:** Keep OS updated, disable Bluetooth when not needed

---

## Security Checklist Before New Device

- [ ] Is this device from a known manufacturer?
- [ ] Did user physically verify the device is nearby?
- [ ] Is there a pairing code to confirm?
- [ ] Is the signal strength reasonable (not suspiciously strong)?
- [ ] Does the device name match expected?

---

## Incident Response

### Unexpected Device Appears
1. Add to `~/bluetooth/pending.md` with timestamp
2. Alert user: "Unknown device 'XX' discovered nearby"
3. Do NOT connect or respond to pairing
4. Log RSSI for potential location analysis

### Command Failure Pattern
1. Log failure details
2. After 3 consecutive failures: alert user
3. Check if device still in range
4. Consider: device compromised? firmware issue?

### Suspected Spoofing
1. Note: same name, different MAC = red flag
2. Alert user immediately
3. Do NOT connect
4. Log all details for analysis

---

## Privacy Considerations

- Bluetooth reveals device presence to anyone scanning
- Your devices' MACs can be used to track you
- Device names often contain personal info (e.g., "John's AirPods")
- **Recommendation:** Use generic device names
- **Recommendation:** Disable Bluetooth when not actively using
