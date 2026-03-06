---
name: lan-scanner
description: Discover devices and scan ports on your local network using nmap
  with security-first defaults.
---


# Network Scanner

Discover devices and scan ports on your local network.

**Use when** scanning LAN, finding devices, or checking open ports.

## Requirements

- `nmap` installed (`apt install nmap` / `brew install nmap`)
- No API keys needed

## Instructions

1. **Determine target** — detect local subnet:
   ```bash
   ip route | grep default | awk '{print $3}' | sed 's/\.[0-9]*$/.0\/24/'
   # or
   ifconfig | grep 'inet ' | grep -v '127.0.0.1'
   ```

2. **⚠️ Validate target — CRITICAL**:
   - ✅ Only scan **private IP ranges**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`
   - ❌ **REJECT public IPs** unless user explicitly confirms ownership
   - Always **confirm scan target** with user before executing

3. **Run scans** (prefer non-root options):

   | Scan Type | Command | Sudo? | Speed |
   |-----------|---------|-------|-------|
   | Host discovery | `nmap -sn {subnet}` | No | Fast |
   | Quick ports | `nmap -F {target}` | No | Fast |
   | All ports | `nmap -p- {target}` | No | Slow |
   | Service detection | `nmap -sV {target}` | No | Medium |
   | OS detection | `sudo nmap -O {target}` | Yes | Medium |
   | Vulnerability scan | `nmap --script vuln {target}` | No | Slow |

4. **Output format**:
   ```
   ## 🔍 Network Scan Results
   **Subnet:** 192.168.1.0/24 | **Date:** YYYY-MM-DD HH:MM
   **Devices found:** 12

   | # | IP | Hostname | MAC | Open Ports | Services |
   |---|-----|----------|-----|-----------|----------|
   | 1 | 192.168.1.1 | router | AA:BB:CC:DD:EE:FF | 80, 443 | HTTP, HTTPS |
   | 2 | 192.168.1.10 | nas | ... | 22, 445, 8080 | SSH, SMB, HTTP |

   ### ⚠️ Security Notes
   - 192.168.1.10: SSH (22) open — ensure key-only auth
   - 192.168.1.15: Telnet (23) open — **insecure, disable if possible**
   ```

5. **Highlight security concerns**:
   - Open Telnet (23) — insecure protocol
   - Open FTP (21) — consider SFTP instead
   - Default HTTP ports with no HTTPS
   - Services on non-standard ports

## Edge Cases

- **nmap not installed**: Suggest installation or fall back to `ping` sweep + `nc` port check.
- **Permission denied**: Non-root can't do SYN scans or OS detection. Note limitations.
- **Firewall blocking**: Some hosts won't respond to ping. Use `-Pn` to skip host discovery.
- **Very large subnet (/16 or larger)**: Warn user it will take a long time. Suggest narrowing scope.
- **VPN active**: Scanned subnet may be the VPN network, not local LAN. Check `ip route`.

## Security Considerations

- **Only scan networks you own or have explicit permission to scan.**
- Unauthorized port scanning may violate laws and terms of service.
- Don't share scan results publicly — they reveal network topology.
- Use `sudo` only when explicitly needed and justified.
