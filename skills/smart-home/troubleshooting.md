# Smart Home Troubleshooting

## Device Offline

### WiFi devices
1. Check if WiFi is working (test with phone)
2. Check if device has power (LED, indicator)
3. Power cycle device (unplug 10 sec, replug)
4. Check router's connected devices list
5. Re-add device to app if still offline

### Zigbee/Z-Wave devices
1. Check batteries if battery-powered
2. Check if hub is online
3. Power cycle hub
4. Check mesh health — is device too far from hub/repeaters?
5. Re-pair device to hub

### After router changes
Most devices need reconfiguration after:
- New router / new WiFi name
- Changed WiFi password
- Moved to different network

---

## Device Won't Pair

### Reset first
- Factory reset the device (see manufacturer instructions)
- Most need: hold button 10-15 sec until LED flashes

### Common reasons pairing fails
| Issue | Solution |
|-------|----------|
| 5GHz vs 2.4GHz | Most smart devices need 2.4GHz — check router settings |
| Too far from hub | Bring device within 10 feet for initial pairing |
| Hub in pairing mode timeout | Restart pairing process |
| Device already paired elsewhere | Full factory reset required |
| Wrong app | Some devices need their own app first, then integrate |

### Still won't pair
1. Try different phone/tablet
2. Try different WiFi network temporarily
3. Check for firmware update on hub
4. Contact manufacturer support

---

## Automation Not Running

### Check triggers
- Is the trigger device online?
- Is the trigger condition actually occurring?
- Check automation history/logs in app

### Check execution
- Is the target device online?
- Manual control works but automation doesn't → check automation config
- Works sometimes → check conditions (time, presence, etc.)

### Common issues
| Symptom | Likely cause |
|---------|--------------|
| Runs late | Cloud delay, use local execution |
| Runs multiple times | Duplicate automations, overlapping triggers |
| Never runs | Device renamed but automation not updated |
| Runs at wrong time | Time zone misconfigured |

---

## Device Responding Slowly

### Possible causes
1. **Cloud dependency** — device goes to cloud and back (500ms+ delay)
2. **WiFi congestion** — too many devices on same channel
3. **Weak signal** — device at edge of WiFi range
4. **Hub overloaded** — too many automations or devices

### Solutions
| Cause | Fix |
|-------|-----|
| Cloud dependency | Switch to local-control hub |
| WiFi congestion | Add access point, change channel, use mesh |
| Weak signal | Add WiFi extender, move device, add Zigbee repeater |
| Hub overload | Split automations, optimize rules |

---

## Device Shows Wrong State

### Examples
- App shows light off, but it's on
- Thermostat shows 72°F but feels colder
- Lock shows locked but it's open

### Causes and fixes
| Issue | Solution |
|-------|----------|
| State not syncing | Power cycle device, force refresh in app |
| Hub lost sync | Restart hub, re-pair device |
| Manual override | Some devices don't report manual changes |
| Sensor drift | Recalibrate (thermostats, sensors) |
| Battery dying | Low battery = erratic behavior, replace |

---

## Emergency Recovery

### Everything offline
1. Check internet — is it your ISP?
2. Check router — power cycle
3. Check hub — power cycle
4. If still down → manual control (physical switches, key locks)

### Lost hub access
- Most hubs have reset button for factory restore
- Cloud-based: check manufacturer's account recovery
- Local-only: may need to reconfigure everything

### Locked out by smart lock
- Always keep physical key backup
- Many locks have manual key override
- Battery compartment usually accessible from outside
