---
name: sys-guard-linux-remediator
description: Host-based Linux incident response and remediation skill focused on precise threat detection, forensic-safe data collection, firewall control (iptables/nftables), integrity validation, and controlled remediation while preserving system stability.
metadata:
  author: Edwin Kairu (ekairu@cmu.edu)
---

# Linux Threat Mitigation and Incident Remediation (Hardened Edition)

This skill provides a structured, forensically-aware framework for analyzing and securing a Linux host during or after a security event.

It emphasizes:

- Non-destructive evidence collection
- Accurate threat detection
- Firewall-aware containment
- Integrity verification
- Controlled, reversible remediation
- Distribution-aware command usage

---

# Environment Context

## Supported Systems

- Debian / Ubuntu
- RHEL / CentOS / Rocky / Alma
- Fedora
- Arch Linux (limited package guidance)

## Execution Assumptions

- Shell: `bash` or POSIX `sh`
- Privilege: Root or sudo
- Host-level access (NOT container-restricted environments)
- systemd-based systems preferred

> ⚠️ If running inside Docker, Kubernetes, LXC, or other containers, firewall, audit, and service commands may not reflect the host system.

---

# Firewall Architecture Awareness

Modern Linux systems may use:

- `iptables-legacy`
- `iptables-nft` (compatibility wrapper)
- Native `nftables`
- `firewalld` (RHEL-family default)

## Identify Firewall Backend

```bash
iptables --version
which nft
systemctl status firewalld
```

If nftables is active:

```bash
nft list ruleset
```

Do NOT assume `iptables -L` represents the full firewall state.

---

# Logging Differences by Distribution

| Distribution | Primary Log File |
|--------------|------------------|
| Ubuntu/Debian | `/var/log/syslog` |
| RHEL/CentOS/Fedora | `/var/log/messages` |
| All modern systemd | `journalctl` |

Always prefer:

```bash
journalctl -xe
```

---

# Operational Toolkit (Hardened)

## 1. Network Inspection

### Listening Services
```bash
ss -tulpn
```

### Active Connections
```bash
ss -antp | grep ESTABLISHED
```

### Firewall State

#### iptables
```bash
iptables -L -n -v --line-numbers
iptables -S
```

#### nftables
```bash
nft list ruleset
```

### Local Service Enumeration (Low Noise)
```bash
ss -lntup
```

Avoid unnecessary full scans of localhost unless required.

### Conservative Network Scan
```bash
nmap -sV -T3 -p- localhost
```

### Packet Capture (Short Snapshot)
```bash
tcpdump -i any -nn -c 100
```

---

## 2. Process & Runtime Analysis

### Process Tree
```bash
ps auxww --forest
```

### High CPU / Memory
```bash
top
```

### Open File Handles
```bash
lsof -p <PID>
```

### System Call Trace (Caution: Alters Timing)
```bash
strace -p <PID>
```

> ⚠️ `strace` may change process behavior. Use carefully during live compromise.

### Kernel Modules
```bash
lsmod
```

### Kernel Messages
```bash
dmesg | tail -50
```

---

## 3. Rootkit & Malware Scanning

### Rootkit Scanners
```bash
rkhunter --check
chkrootkit
```

> May produce false positives. Validate findings manually.

### Antivirus Scan (Targeted)
```bash
clamscan -r /home
```

Use selectively; large scans increase I/O and may alter access timestamps.

### Lynis System Audit
```bash
lynis audit system
```

---

## 4. File Integrity & Package Verification

### AIDE (After Initialization)

Install:
```bash
apt install aide
# or
dnf install aide
```

Initialize:
```bash
aideinit
mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```

Run Check:
```bash
aide --check
```

### RHEL Package Verification
```bash
rpm -Va
```

### Debian Package Verification
```bash
apt install debsums
debsums -s
```

---

## 5. Forensic Analysis (Didier Stevens Suite)

Install:

```bash
sudo mkdir -p /opt/forensics
sudo wget -P /opt/forensics https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/base64dump.py
sudo wget -P /opt/forensics https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/re-search.py
sudo wget -P /opt/forensics https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/zipdump.py
sudo wget -P /opt/forensics https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/1768.py
sudo wget -P /opt/forensics https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/pdf-parser.py
sudo wget -P /opt/forensics https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/oledump.py
sudo chmod +x /opt/forensics/*.py
```

### Decode Base64
```bash
python3 /opt/forensics/base64dump.py file.txt
```

### IOC Search
```bash
python3 /opt/forensics/re-search.py -n ipv4 logfile
```

### Inspect ZIP (No Extraction)
```bash
python3 /opt/forensics/zipdump.py suspicious.zip
```

### Extract Cobalt Strike Beacon Config
```bash
python3 /opt/forensics/1768.py payload.bin
```

### Inspect Office/PDF Documents
```bash
python3 /opt/forensics/pdf-parser.py file.pdf
python3 /opt/forensics/oledump.py file.doc
```

> Static inspection only. Never execute suspicious files.

---

## 6. Authentication & User Activity

### Current Sessions
```bash
who -a
```

### Login History
```bash
last -a
```

### Failed SSH Logins

Ubuntu/Debian:
```bash
journalctl -u ssh.service | grep "Failed password"
```

RHEL/Fedora:
```bash
journalctl -u sshd.service | grep "Failed password"
```

### Sudo Activity
```bash
journalctl _COMM=sudo
```

### Audit Logs
```bash
ausearch -m USER_AUTH,USER_LOGIN,USER_CHAUTHTOK
```

---

# Controlled Remediation

## Blocking an IP

### iptables (Immediate)
```bash
iptables -I INPUT 1 -s <IP> -j DROP
```

### nftables
```bash
nft add rule inet filter input ip saddr <IP> drop
```

If firewalld is active:
```bash
firewall-cmd --add-rich-rule='rule family="ipv4" source address="<IP>" drop'
```

---

## Persisting Firewall Rules

iptables (Debian):
```bash
netfilter-persistent save
```

iptables (manual save):
```bash
iptables-save > /etc/iptables/rules.v4
```

firewalld:
```bash
firewall-cmd --runtime-to-permanent
```

nftables:
```bash
nft list ruleset > /etc/nftables.conf
```

---

## Process Containment Strategy

Preferred escalation:

1. Observe
2. `kill -TERM <PID>`
3. If required: `kill -STOP <PID>` for analysis
4. Use `kill -KILL <PID>` only if necessary

Avoid `killall` or broad `pkill`.

---

## Service Isolation

```bash
systemctl stop <service>
systemctl disable <service>
systemctl mask <service>
```

---

# Persistence & Backdoor Checks

### Cron Jobs
```bash
crontab -l
ls -lah /etc/cron*
```

### Systemd Persistence
```bash
ls -lah /etc/systemd/system/
```

### Startup Scripts
```bash
cat /etc/rc.local
```

---

# SELinux Awareness (RHEL/Fedora)

Check status:
```bash
getenforce
```

Review denials:
```bash
ausearch -m AVC
```

---

# Forensic Hygiene

1. Never execute suspicious binaries.
2. Preserve evidence before deletion:

```bash
sha256sum file
mkdir -p /root/quarantine
mv file /root/quarantine/file.vir
```

3. Log every remediation step:

```bash
date -u
```

Document:
- Timestamp
- Command executed
- Observed outcome

---

# Usage Examples

## Routine Audit

- Run `lynis audit system`
- Verify no unknown listening services
- Check for modified system binaries

## Active Threat

- Identify high CPU process
- Capture short `tcpdump`
- Extract file hash
- Contain IP via firewall
- Preserve malicious artifact

## Suspicious File

- Use `zipdump`
- Extract hash
- Move to quarantine
- Search logs for execution attempts

---

# Safety Guardrails

These guardrails are mandatory and apply to all remediation activity. Their purpose is to prevent self-inflicted outages, preserve forensic integrity, and ensure reversible, controlled incident response.

---

## 1. State Verification (Pre- and Post-Change Validation)

Before executing any remediation command:

1. Record timestamp (UTC):
   ```bash
   date -u
   ```

2. Run a discovery command to capture current state:
   - Network: `ss -tulpn`
   - Active connections: `ss -antp`
   - Firewall (iptables): `iptables -L -n -v`
   - Firewall (nftables): `nft list ruleset`
   - firewalld: `firewall-cmd --list-all`

After remediation:

3. Re-run the same discovery command.
4. Compare state change and confirm:
   - Intended effect achieved
   - No unintended service disruption
   - No management lockout (e.g., SSH access intact)

Never assume a command succeeded without verifying its effect.

---

## 2. No Wildcards or Broad Termination

To prevent catastrophic system damage:

- NEVER use:
  - `rm -rf *`
  - `rm -rf /`
  - `killall`
  - Broad `pkill` patterns
  - Unbounded globbing in sensitive directories

- Always:
  - Use absolute file paths (e.g., `/tmp/malware.bin`)
  - Target explicit PIDs (`kill -TERM <PID>`)
  - Confirm file existence with `ls -lah <file>`
  - Hash suspicious files before modification:
    ```bash
    sha256sum <file>
    ```

Wildcard deletions and pattern-based termination are prohibited during incident response.

---

## 3. Persistence & Re-Spawn Inspection

After containment of a malicious process or service, immediately inspect for persistence mechanisms.

### Check:

#### Cron Jobs
```bash
crontab -l
ls -lah /etc/cron*
```

#### systemd Services & Timers
```bash
systemctl list-unit-files --type=service
systemctl list-timers --all
ls -lah /etc/systemd/system/
```

#### Init Scripts
```bash
ls -lah /etc/init.d/
cat /etc/rc.local
```

#### User-Level Persistence
```bash
ls -lah ~/.config/systemd/user/
```

#### SSH Backdoors
```bash
cat ~/.ssh/authorized_keys
```

After removal of malicious artifacts:

- Run integrity verification:
  ```bash
  aide --check
  ```
- On RHEL-based systems:
  ```bash
  rpm -Va
  ```
- On Debian-based systems:
  ```bash
  debsums -s
  ```

Do not consider a threat eradicated until persistence mechanisms are eliminated.

---

## 4. Firewall Rule Safety & Persistence

### A. Anti-Lockout Requirement

Before modifying firewall rules:

1. Confirm SSH listening port:
   ```bash
   ss -tulpn | grep ssh
   ```

2. Confirm an explicit ACCEPT rule exists for:
   - Current management IP
   - SSH port

NEVER:
```bash
iptables -F
```

NEVER set a default DROP policy without verifying SSH access rule exists.

---

### B. Immediate vs Persistent Rules

Firewall rule changes are runtime by default and may not survive reboot.

#### iptables (Debian/Ubuntu)
Runtime only until saved:
```bash
iptables-save > /etc/iptables/rules.v4
```

If using netfilter-persistent:
```bash
netfilter-persistent save
```

#### RHEL (legacy iptables service)
```bash
service iptables save
```

#### firewalld
Runtime-to-permanent:
```bash
firewall-cmd --runtime-to-permanent
```

#### nftables
Persist ruleset:
```bash
nft list ruleset > /etc/nftables.conf
```

Document:
- Whether rule is temporary or permanent
- Location of saved configuration
- Verification after reboot (if applicable)

---

## 5. Forensic Preservation Before Destruction

Before deleting or killing:

1. Hash the artifact:
   ```bash
   sha256sum <file>
   ```

2. Move to quarantine:
   ```bash
   mkdir -p /root/quarantine
   mv <file> /root/quarantine/<file>.vir
   ```

3. Record:
   - Timestamp (UTC)
   - Original path
   - Hash value
   - Reason for containment

Avoid `kill -9` unless absolutely required. Prefer:

1. `kill -TERM <PID>`
2. `kill -STOP <PID>` (if forensic inspection needed)
3. `kill -KILL <PID>` only as last resort

---

## 6. Change Logging Requirement

Every remediation action must include:

- `date -u`
- Command executed
- Justification
- Observed outcome
- Updated risk level (if applicable)

Remediation without documentation is non-compliant.

---

## 7. Minimal-Impact Principle

All actions must follow:

- Smallest necessary change
- Reversible where possible
- No broad configuration resets
- No service restarts without justification
- No system-wide scans during active compromise unless scoped

Contain first. Eradicate methodically. Recover cautiously.

