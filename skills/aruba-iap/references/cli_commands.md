# Aruba IAP CLI Complete Command Reference

Complete command reference for Aruba Instant AP (IAP) Command Line Interface.

## Command Categories

### Configuration Commands

#### System Configuration

```bash
# Hostname
hostname <name>

# Domain name
ip domain-name <domain>

# Name servers
ip name-server <ip-addr>

# IP address configuration
ip address <ip> <netmask>
ip default-gateway <ip>
ip address dhcp

# Timezone
clock timezone <timezone>
```

#### WLAN Configuration

```bash
# Create/modify WLAN
wlan <wlan-id>
ssid <ssid-name>
broadcast-ssid {enable|disable}
security {open|wep|wpa2-psk|wpa2-enterprise|wpa3-psk}
wpa2-passphrase <passphrase>
wpa2-enterprise-key <key>
wpa3-passphrase <passphrase>
vlan-id <vlan-id>
opmode {access|tunnel|wds}
auth-server <server-ip>
```

#### Interface Configuration

```bash
# Enter interface mode
interface <interface-name>
switchport mode {access|trunk}
switchport access vlan <vlan-id>
switchport trunk allowed-vlan <vlan-list>
no shutdown
shutdown
```

#### Radio Configuration

```bash
# Radio settings
radio {2.4GHz|5GHz}
channel <channel>
channel-width {20|40|80|160}
tx-power-level <level>
dfs-enable {enable|disable}
```

### Show Commands

#### System Status

```bash
show version
show running-config
show startup-config
show license
show boot
```

#### AP Status

```bash
show ap database
show ap client
show ap config
show ap upgrade
show ap health
```

#### Network Status

```bash
show ip interface
show ip route
show ip arp
show ip dhcp
show ip dns
```

#### Wireless Status

```bash
show wlan
show radio
show ap client trail-info <client-mac>
show auth-tracebuf
show ap client reassociation
```

#### User Management

```bash
show user-table
show mgmt-user
show admin-password
```

### Diagnostic Commands

```bash
# Network diagnostics
ping <ip-address>
ping count <number>
ping size <size>
ping timeout <seconds>

# Route tracing
traceroute <ip-address>
traceroute max-hops <number>

# DNS lookup
nslookup <hostname>

# HTTP/HTTPS test
http-test <url>
https-test <url>
```

### Clear Commands

```bash
# Clear ARP table
clear ip arp

# Clear clients
clear ap client <mac-address>
clear ap client all

# Clear user table
clear user-table

# Clear statistics
clear ap statistics
clear radio statistics
```

### Cluster Management Commands

```bash
# Virtual Controller commands
ap-group <group-name>
master-redundancy enable
master-redundancy disable
convert-aos-ap <controller-ip>
convert-aos-ap-local
```

### Security Commands

```bash
# Management access
security-management enable
security-management disable
mgmt-user <username> privilege <level>

# Firewall rules
firewall policy <policy-name>
firewall rule <rule-id>
```

## Command Examples

### Example 1: Basic SSID Setup

```bash
ap-name# configure
ap-name(config)# wlan 1
ap-name(config-wlan)# ssid MyWiFi
ap-name(config-wlan)# security wpa2-psk
ap-name(config-wlan)# wpa2-passphrase SecurePassword123
ap-name(config-wlan)# broadcast-ssid enable
ap-name(config-wlan)# exit
ap-name(config)# write memory
```

### Example 2: VLAN Trunking

```bash
ap-name# configure
ap-name(config)# interface port1
ap-name(config-if)# switchport mode trunk
ap-name(config-if)# switchport trunk allowed-vlan 10,20,30
ap-name(config-if)# no shutdown
```

### Example 3: Client Troubleshooting

```bash
ap-name# show ap client
# Output shows all connected clients with MAC, IP, and RSSI

ap-name# show ap client trail-info aa:bb:cc:dd:ee:ff
# Output shows client association history
```

### Example 4: Network Diagnostics

```bash
ap-name# ping 8.8.8.8
ap-name# traceroute 8.8.8.8
ap-name# nslookup google.com
```

## Command Tips

1. **Tab Completion**: Use Tab for command completion
2. **Help**: `?` shows available commands, `command ?` shows command options
3. **No Prefix**: `no <command>` disables/removes configuration
4. **Config Change**: Most changes require `write memory` or `commit`
5. **Exit**: `exit` or `Ctrl+Z` to exit current mode

## Version-Specific Commands

### Aruba Instant 6.x
- Basic AP clustering
- AirGroup support
- Limited WiFi 6 features

### Aruba Instant 8.x
- Full WiFi 6 (802.11ax) support
- Enhanced roaming
- Better security features

### Aruba AOS 10.x
- Cloud management features
- Enhanced security (WPA3)
- Improved diagnostics
