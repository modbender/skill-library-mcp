# Aruba IAP Best Practices

Deployment, configuration, and operational best practices for Aruba Instant AP networks.

## Planning Phase

### Site Survey

1. **Physical Survey**
   - Use professional site survey tools
   - Map coverage areas and RF heatmaps
   - Identify interference sources
   - Mark AP locations accurately

2. **Capacity Planning**
   - Calculate expected client density
   - Plan for peak usage (2-3x average)
   - Consider future expansion (20% buffer)

3. **Network Design**
   - Design VLAN structure
   - Plan IP addressing scheme
   - Define routing and firewall rules

### AP Placement

**Spacing Guidelines:**

| Environment | AP Spacing | Coverage Radius |
|------------|-------------|----------------|
| Office (high density) | 30-40 ft (10-12 m) | 50-60 ft (15-18 m) |
| Office (low density) | 50-60 ft (15-18 m) | 80-100 ft (24-30 m) |
| Warehouse/Manufacturing | 80-100 ft (24-30 m) | 120-150 ft (36-45 m) |
| Outdoor | 150-200 ft (45-60 m) | 200-250 ft (60-75 m) |

**Placement Tips:**
- Mount APs at ceiling height where possible
- Avoid obstacles between AP and coverage area
- Orient antennas perpendicular to target area
- Consider mounting for future access

## Configuration Best Practices

### SSID Configuration

1. **Separate Networks**
   - Corporate SSID for employees
   - Guest SSID for visitors
   - IoT SSID for devices
   - Each with appropriate security level

2. **SSID Naming Convention**
   - Use descriptive names (e.g., "Corp-Floor1", "Guest-Lobby")
   - Include location or floor if multiple
   - Avoid special characters
   - Keep under 32 characters

3. **Security by Use Case**

| Use Case | Recommended Security |
|----------|------------------|
| Corporate | WPA2-Enterprise or WPA3 with 802.1X |
| Guest | WPA2-PSK with captive portal or open |
| IoT | WPA2-PSK with device auth |
| High-security | WPA3 with 802.1X + Certificate |

### Security Configuration

**Authentication Methods:**

| Method | Best For | Notes |
|---------|-----------|-------|
| **Open** | Guest networks only | Not recommended for production |
| **WPA2-PSK** | Small office, home | Simple, no RADIUS required |
| **WPA2-Enterprise** | Enterprise | Use with RADIUS server |
| **WPA3-SAE** | Modern security | Best for new deployments |

**RADIUS Configuration:**
```bash
# Configure RADIUS server
(config-wlan)# auth-server <RADIUS-IP>
(config-wlan)# auth-server port <port>
(config-wlan)# auth-server secret <shared-secret>

# Use 802.1X authentication
(config-wlan)# security wpa2-enterprise
(config-wlan)# security eap-type <method>
```

### VLAN Design

**VLAN Best Practices:**

1. **Logical Separation**
   - Voice VLAN (VLAN 100)
   - Data VLAN (VLAN 10)
   - Guest VLAN (VLAN 20)
   - Management VLAN (VLAN 99, native)

2. **Tagging Configuration**
   ```bash
   # Access port
   interface port1
   switchport mode access
   switchport access vlan 10

   # Trunk port (multi-VLAN)
   interface port2
   switchport mode trunk
   switchport trunk allowed-vlan 10,20,100
   ```

3. **QoS Prioritization**
   - Voice: Priority 7 (DSCP EF)
   - Video: Priority 5 (DSCP AF41)
   - Data: Priority 3 (DSCP AF11)

### Radio Configuration

**Channel Planning:**

| Environment | Channels (2.4 GHz) | Channels (5 GHz) |
|------------|-------------------|----------------|
| High density | 1, 6, 11 | 36, 40, 44, 48, 149, 153 |
| Low density | 1, 6, 11 | 36, 40, 44, 48, 149, 153 |
| Interference prone | 3, 8, 11 | 149, 153, 157, 161, 165 |

**Power Settings:**

| Environment | Power Level | Notes |
|------------|-------------|-------|
| Indoor office | Medium (40-60%) | Balance coverage and interference |
| High density | Low-Medium (30-50%) | Reduce co-channel interference |
| Warehouse/High ceiling | High (70-100%) | Maximize coverage |
| Multi-AP deployment | Auto (AMC) | Use Adaptive Power Management |

## Deployment Workflow

### 1. Pre-Deployment Checklist

- [ ] Site survey completed
- [ ] Network design finalized
- [ ] IP addressing plan ready
- [ ] VLAN allocation defined
- [ ] SSID naming convention established
- [ ] RADIUS server configured (if needed)
- [ ] Firmware updates reviewed
- [ ] Hardware inventory complete

### 2. Initial Configuration

```bash
# 1. Factory reset (if needed)
write erase startup-config
reload

# 2. Basic network setup
configure
hostname <location-F1>
ip address <ip> <netmask>
ip default-gateway <gateway>
ip name-server <dns-server>
exit
write memory

# 3. Configure WLANs
configure
wlan corporate
ssid Corporate
security wpa2-enterprise
auth-server <RADIUS-IP>
vlan-id 10
exit

wlan guest
ssid Guest
security wpa2-psk
wpa2-passphrase <password>
vlan-id 20
exit
write memory
```

### 3. Post-Deployment Verification

```bash
# Verify AP sees controller (if applicable)
show ap database

# Check connectivity
ping <controller-ip>

# Verify SSIDs are broadcasting
show wlan

# Test client connectivity
# Connect test client to each SSID
show ap client

# Check radio health
show radio
```

### 4. Documentation

Document each deployment:
- AP serial numbers
- MAC addresses
- IP addresses
- Firmware versions
- Configuration details
- Site maps
- AP locations

## Operational Best Practices

### Monitoring

**Daily Checks:**
```bash
# AP health
show ap health

# Client count
show ap client

# Radio status
show radio

# Error logs
show logging | include error
```

**Weekly Checks:**
```bash
# Performance metrics
show ap statistics
show radio statistics

# Configuration drift
show running-config
show startup-config

# License status
show license
```

### Maintenance

**Regular Tasks:**

| Frequency | Task | Notes |
|----------|------|-------|
| Weekly | Review logs | Check for errors/warnings |
| Monthly | Review client count | Identify capacity issues |
| Quarterly | Update firmware | Check for security patches |
| Bi-annual | Site survey | Coverage and interference review |
| Annually | Hardware audit | Replace aging equipment |

### Backup Strategy

**What to Backup:**
- Running configuration
- Startup configuration
- SSID profiles
- Security settings
- RADIUS server configs

**Backup Methods:**

1. **Manual CLI Backup:**
   ```bash
   terminal length 0
   show running-config
   ```

2. **Automated Script:**
   ```bash
   python3 scripts/config_backup.py <AP-IP> backup-<date>.txt
   ```

3. **Web Interface:**
   - Navigate to AP web UI
   - Configuration → Backup Configuration

**Backup Frequency:**
- Before major changes
- After firmware upgrades
- Weekly (automated)
- Monthly (full archive)

## Security Best Practices

### Access Control

1. **Use Least Privilege**
   - Create admin accounts only for authorized personnel
   - Use read-only accounts for monitoring
   - Rotate passwords regularly (90 days)

2. **Network Segmentation**
   - Separate management VLAN
   - Isolate guest networks
   - Use ACLs to restrict access

3. **Account Lockout**
   ```bash
   # Enable account lockout
   security-management
   mgmt-user admin privilege 15 lockout-duration 30
   ```

### Wireless Security

1. **Encryption Standards**
   - Use WPA3 for new deployments
   - WPA2-Enterprise for corporate
   - Never use WEP or WPA (deprecated)

2. **Authentication**
   - Implement 802.1X for enterprise
   - Use RADIUS for centralized auth
   - Enable certificate-based auth where possible

3. **Guest Networks**
   - Isolate on separate VLAN
   - Use captive portal
   - Time-limited access (8 hours recommended)

## Troubleshooting Best Practices

### Systematic Approach

1. **Gather Information**
   - What changed recently?
   - How many APs affected?
   - What time did issues start?

2. **Isolate Scope**
   - Single AP or multiple?
   - Specific feature or overall?
   - Wired network or wireless?

3. **Check Logs**
   ```bash
   # Recent errors
   show logging | include error

   # Client issues
   show ap client trail-info <mac>
   ```

4. **Test Changes**
   - Rollback if issues started after change
   - Test one change at a time
   - Document rollback process

### Common Issue Resolution

| Issue | First Check | Second Check | Resolution |
|---------|-------------|--------------|------------|
| No clients | `show radio` | `show wlan` | Enable radio/SSID |
| Slow speeds | `show ap client` | Channel survey | Change channel/power |
| Can't connect | Ping test | `show logging` | Check security settings |
| Cluster issues | `show ap-group` | Network connectivity | Re-provision APs |

## Performance Optimization

### Client Density

**Recommended Clients per AP:**

| Environment | Max Clients |
|------------|-------------|
| High density office | 60-80 |
| Standard office | 40-60 |
| Low density | 20-40 |
| Guest area | 80-100 |

**Signs of Overload:**
- High CPU usage (>80%)
- Slow authentication
- Client disconnections
- Poor throughput

**Mitigation:**
- Add additional APs
- Reduce power on overlapping APs
- Implement load balancing

### Roaming Optimization

**Settings for Seamless Roaming:**
```bash
# Enable 802.11k/v Fast Roaming
configure
wlan <name>
enable-fast-roaming enable
exit
write memory

# Configure roaming threshold
configure
ap-group <name>
roaming-threshold <rssi-value>
```

**Best Practices:**
- Use consistent SSIDs across APs
- Match security settings
- Proper channel separation
- Optimize AP density

## Upgrade Best Practices

### Firmware Upgrade Process

1. **Pre-Upgrade**
   - Check release notes
   - Download correct firmware version
   - Backup current configuration
   - Plan maintenance window

2. **Upgrade**
   ```bash
   # Check current version
   show version

   # Download and upload firmware
   # (via Web UI or TFTP)
   ```

3. **Post-Upgrade**
   - Verify all features work
   - Compare running vs startup config
   - Monitor for 24 hours
   - Have rollback plan ready

### Testing Before Production

1. **Lab Environment**
   - Test configuration changes in lab
   - Verify client compatibility
   - Check for regressions

2. **Staged Rollout**
   - Deploy to one AP first
   - Monitor for issues
   - Rollout to remaining APs

## Documentation Best Practices

### Configuration Documentation

Keep records of:
- IP address scheme
- VLAN allocations
- SSID definitions
- Security settings
- RADIUS configuration
- Firewall rules

### Change Management

For every change, document:
- Date and time
- Changed by (person/system)
- What was changed
- Reason for change
- Expected outcome
- Rollback procedure

### Network Diagrams

Maintain updated diagrams showing:
- AP locations
- Cabling
- VLAN structure
- Routing topology
- Internet edge

## Compliance and Standards

### Industry Standards

- **802.11ax (WiFi 6)**: Latest standard, use for new deployments
- **WPA3**: Required for best security
- **802.1X**: Required for enterprise authentication

### Regulatory Compliance

- **DFS (Dynamic Frequency Selection)**: Required in most regions
- **TPC (Transmit Power Control)**: Compliance requirement
- **Country Code**: Set correctly for region

## Summary Checklist

### Pre-Deployment
- [ ] Site survey completed
- [ ] Network design approved
- [ ] Hardware procured
- [ ] IP addressing planned
- [ ] VLAN allocation defined
- [ ] Security policy defined
- [ ] Backup plan established

### During Deployment
- [ ] Configure basic network settings
- [ ] Set up WLANs/SSIDs
- [ ] Configure security
- [ ] Test client connectivity
- [ ] Verify cluster operation

### Post-Deployment
- [ ] Document all configurations
- [ ] Create network diagrams
- [ ] Set up monitoring
- [ ] Train staff
- [ ] Establish maintenance schedule

---

For more information, see:
- [Aruba Documentation](https://arubanetworking.hpe.com/techdocs)
- [Aruba Community](https://community.arubanetworks.com)
