# Smart Home Security & Privacy

## Network Isolation (VLAN Setup)

### Why it matters
One compromised smart bulb shouldn't access your laptop, NAS, or banking sessions. IoT devices are attack vectors.

### Basic setup (most routers)
1. Create guest network for IoT devices
2. Disable "guest can access local network" if available
3. All smart devices connect to guest network
4. Your phones/laptops stay on main network

### Advanced setup (prosumer routers)
1. Create dedicated IoT VLAN (e.g., VLAN 30)
2. Firewall rules:
   - IoT → Internet: ALLOW
   - IoT → Main LAN: DENY
   - Main LAN → IoT: ALLOW (for control)
3. Separate SSID for IoT VLAN
4. All smart devices connect to IoT SSID

### Hub placement
The hub (Home Assistant, SmartThings, etc.) needs to talk to both networks:
- Option A: Hub on main network with firewall exception
- Option B: Hub on IoT network, access via reverse proxy

---

## Local-First Options

### Controllers (no cloud required)
| System | Cloud Required | Local Control |
|--------|----------------|---------------|
| Home Assistant | No | Full |
| Hubitat | No | Full |
| HomeKit | Partial (sync) | Yes |
| SmartThings | Yes | Limited |
| Google Home | Yes | No |
| Alexa | Yes | No |

### Devices that work offline
- Zigbee devices with local hub
- Z-Wave devices with local hub
- Lutron Caseta (with local API)
- Most Thread/Matter devices
- Shelly (local API, no cloud needed)

### Devices that require cloud
- Most WiFi cameras (Ring, Nest, Wyze)
- Ecobee thermostats
- August locks
- Most cheap Tuya/SmartLife devices

---

## Credential Hygiene

### Must change from defaults
- [ ] Router admin password
- [ ] Hub admin password
- [ ] Camera streaming passwords
- [ ] Lock PINs (not 1234, 0000, birthday)
- [ ] WiFi password (used by all devices)

### Account security
- [ ] MFA on: lock apps, camera apps, thermostat apps, hub dashboards
- [ ] Unique passwords per service (password manager)
- [ ] Recovery email secured with MFA
- [ ] Check for account sharing — remove old family members/guests

---

## Privacy Considerations

### Voice assistants
- Review and delete voice history periodically
- Use physical mute button when not in use
- Consider local-only alternatives (Home Assistant voice)

### Cameras
- Local storage (NAS, SD card) vs cloud
- Disable audio recording if only video needed
- Point cameras away from neighbor property
- Check local laws on recording

### Data collection
- Read privacy policies before buying
- Opt out of data sharing where possible
- Prefer devices with local-only options
- Avoid devices from companies with poor track records

---

## Monthly Security Checklist

- [ ] Router firmware updated
- [ ] Hub firmware updated
- [ ] Check for new device firmware
- [ ] Review connected devices list (remove unknowns)
- [ ] Review user access (remove old codes/accounts)
- [ ] Check cloud service breach notifications
- [ ] Verify MFA still active on critical accounts
