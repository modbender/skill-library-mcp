# Aruba IAP Troubleshooting Guide

Comprehensive troubleshooting guide for Aruba Instant AP issues.

## Table of Contents

1. [Connectivity Issues](#connectivity-issues)
2. [Client Connection Problems](#client-connection-problems)
3. [Performance Issues](#performance-issues)
4. [Cluster Problems](#cluster-problems)
5. [Firmware Issues](#firmware-issues)
6. [Security Issues](#security-issues)

## Connectivity Issues

### AP Not Getting IP Address

**Symptoms:**
- AP shows IP as 0.0.0.0
- Unable to access AP via SSH/Web

**Diagnosis:**
```bash
# Check interface status
show ip interface

# Check DHCP server
ping <DHCP-server-IP>

# Verify DHCP options (option 43 for controller discovery)
```

**Solutions:**
1. Verify network cable connection
2. Check DHCP server is running
3. Verify DHCP option 43 configuration for controller
4. Restart AP: `reload`

### AP Cannot Connect to Controller/Central

**Symptoms:**
- AP gets IP but shows as "Not Provisioned"
- AP not visible in Aruba Central

**Diagnosis:**
```bash
# Check controller connectivity
ping <controller-IP>

# Check DNS resolution
nslookup <controller-hostname>

# Check firewall rules (ports 4343/5247)
```

**Solutions:**
1. Verify firewall allows controller ports
2. Check DNS settings
3. Re-provision AP: `convert-aos-ap <controller-IP>`
4. Verify controller license capacity

### Intermittent Connectivity

**Symptoms:**
- AP goes online/offline randomly
- SSH sessions drop frequently

**Diagnosis:**
```bash
# Check boot status
show boot

# Check error logs
show logging | include error

# Monitor uptime
show system
```

**Solutions:**
1. Replace network cable
2. Check power supply stability
3. Update firmware
4. Check for environmental interference

## Client Connection Problems

### Clients Cannot See SSID

**Symptoms:**
- SSID not visible
- SSID visible but cannot connect

**Diagnosis:**
```bash
# Check SSID broadcast
show wlan

# Check radio status
show radio

# Check channel utilization
show ap client
```

**Solutions:**
1. Verify SSID broadcast enabled: `broadcast-ssid enable`
2. Check radio is enabled: `no shutdown` on radio interface
3. Verify channel not overlapping
4. Check security settings match on client

### High Authentication Failures

**Symptoms:**
- Clients fail WPA2 authentication
- 802.1X auth failures

**Diagnosis:**
```bash
# Check security configuration
show running-config | include security

# Check RADIUS server (if used)
ping <RADIUS-server-IP>
show auth-tracebuf
```

**Solutions:**
1. Verify passphrase is correct
2. Check security type (WPA2 vs WPA3)
3. Verify RADIUS server is reachable
4. Check authentication server configuration

### Slow Client Performance

**Symptoms:**
- Low throughput
- High latency
- Packet loss

**Diagnosis:**
```bash
# Check client RSSI
show ap client

# Check radio statistics
show radio

# Check channel interference
show ap scan
```

**Solutions:**
1. Optimize channel selection
2. Reduce co-channel interference
3. Check for microwave/Bluetooth interference
4. Consider AP placement

## Performance Issues

### High CPU Usage

**Symptoms:**
- CPU usage > 80%
- Slow response to CLI

**Diagnosis:**
```bash
# Check system resources
show system

# Check client count
show ap client

# Check for broadcast storms
show logging | include warning
```

**Solutions:**
1. Enable broadcast suppression
2. Disable unnecessary features
3. Reduce client density per AP
4. Upgrade to higher-capacity AP

### High Memory Usage

**Symptoms:**
- Memory usage > 80%
- AP becomes unstable

**Diagnosis:**
```bash
# Check memory
show system

# Check for memory leaks
show process
```

**Solutions:**
1. Restart AP: `reload`
2. Update firmware
3. Reduce enabled features
4. Check for memory leak bugs in release notes

## Cluster Problems

### Master Election Issues

**Symptoms:**
- Multiple APs claiming to be master
- Configuration not syncing

**Diagnosis:**
```bash
# Check cluster status
show ap-group

# Check master status
show ap database

# Check AP roles
show ap config
```

**Solutions:**
1. Manually set master: `ap-group <name> master <mac>`
2. Enable master redundancy: `master-redundancy enable`
3. Ensure all APs on same subnet
4. Verify all APs have same firmware

### Configuration Sync Issues

**Symptoms:**
- Config changes not applying to all APs
- Inconsistent configuration across cluster

**Diagnosis:**
```bash
# Show running config on master
show running-config

# Show running config on slaves
# SSH to slave AP and check config
```

**Solutions:**
1. Make changes only on master AP
2. Verify all APs are in same group
3. Force config sync: `write memory` on master
4. Check network connectivity between APs

## Firmware Issues

### Upgrade Failed

**Symptoms:**
- Firmware upgrade hangs
- AP stuck in boot loop

**Diagnosis:**
```bash
# Check current version
show version

# Check boot status
show boot
```

**Solutions:**
1. Verify firmware file integrity
2. Use wired network for upgrade
3. Factory reset and retry
4. Contact support if persists

### Downgrade Required

**Symptoms:**
- New firmware causes issues
- Feature regression

**Solutions:**
1. Download previous firmware version
2. Upload via web interface
3. Use `reload` after downgrade
4. Test thoroughly before upgrade

## Security Issues

### Cannot Access Management Interface

**Symptoms:**
- SSH refused
- Web interface timeout

**Diagnosis:**
```bash
# Check management access
show mgmt-user

# Check security settings
show running-config | include security
```

**Solutions:**
1. Verify username/password
2. Check IP restrictions
3. Check firewall allows management ports
4. Enable necessary management protocols

### Rogue AP Detection

**Symptoms:**
- Unknown APs detected
- Clients connecting to wrong AP

**Diagnosis:**
```bash
# Check for rogue APs
show ap scan
show ap database
```

**Solutions:**
1. Enable WIDS (Wireless Intrusion Detection)
2. Configure rogue AP classification
3. Set up containment policies
4. Regularly monitor AP scan results

## Diagnostic Commands Quick Reference

### Health Check
```bash
# Overall status
show ap health
show system

# Network tests
ping <gateway>
traceroute <internet-ip>
nslookup <external-host>

# Wireless tests
show ap client
show radio
show wlan
```

### Log Analysis
```bash
# Recent errors
show logging | include error

# Recent warnings
show logging | include warning

# All logs
show logging | all
```

### Configuration Verification
```bash
# Compare running vs startup
show running-config
show startup-config

# Check specific settings
show wlan
show interface
show ip interface
```

## When to Contact Support

If issues persist after trying these steps:

1. Collect diagnostic output
2. Save configuration backup
3. Note firmware version
4. Document steps taken
5. Contact HPE Aruba Support with case details

### Support Information

- **Aruba Community**: https://community.arubanetworks.com
- **HPE Support**: https://support.hpe.com/hpesc/public/docDisplay
- **Aruba Central**: https://arubanetworking.hpe.com/central

## Proactive Monitoring

Set up regular checks:

```bash
# Weekly checks
show ap health
show ap client
show radio

# Monthly reviews
show version
show license
show running-config
```

Use [scripts/monitor_clients.py](../scripts/monitor_clients.py) for automated monitoring.
