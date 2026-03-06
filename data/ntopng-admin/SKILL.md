---
name: ntopng-admin
description: Professional network monitoring and device identification using ntopng Redis data. Designed for security auditing and diagnostic environments.
metadata:
  openclaw:
    disableModelInvocation: true
    requires:
      bins: ["ssh", "jq"]
      env: ["OPNSENSE_HOST", "OPNSENSE_SSH_PORT", "NTOP_INSECURE"]
---

# ntopng Network Monitor (Secure Edition)

A powerful network auditing tool that queries ntopng data directly from Redis via a secure SSH tunnel. This skill is built for network administrators and security professionals who need high-visibility into local network traffic.

## ⚠️ High Privilege Warning & Responsible Use

**PROCEED WITH CAUTION:** This skill performs high-privilege operations, including executing commands on your network gateway via SSH and reading internal network states. 

1.  **Strict Audit Only:** Intended for Lab, Test, or controlled Audit environments. Avoid use in critical production systems unless the agent's access is strictly isolated.
2.  **Explicit Consent:** By default, autonomous invocation is disabled. You must manually approve each query to maintain full oversight of the data being accessed.
3.  **Security Posture:** This tool uses SSH Key Authentication. Never use plain-text passwords. Ensure your SSH keys are protected with passphrases where applicable.
4.  **Data Sensitivity:** Be aware that this tool exposes MAC addresses, internal IPs, and connection metadata. Handle output with the same care as your network configuration files.

## Prerequisites

*   **SSH Key Access:** Public key authentication must be configured between the OpenClaw host and the OPNsense/ntopng host.
*   **Binaries:** `ssh` and `jq` must be available in the local environment.
*   **Backend:** ntopng must be running with Redis persistence enabled on the target host.

## Configuration

Declare these variables in your environment or agent configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPNSENSE_HOST` | Target gateway IP or hostname | `192.168.1.1` |
| `OPNSENSE_SSH_PORT` | SSH service port | `50222` |
| `NTOP_INSECURE` | Set to `true` for self-signed certificates (if applicable) | `false` |

## Available Commands

The helper script `scripts/ntopng-helper.sh` provides safe, read-only data extraction:

### 1. Network Inventory
```bash
./scripts/ntopng-helper.sh list [limit]
```
Lists detected devices with MAC, IP, total traffic volume, and last-seen timestamps.

### 2. Device Forensics
```bash
./scripts/ntopng-helper.sh device-info <ip|mac>
```
Provides granular traffic breakdown, packet counts, and inferred device classification.

### 3. Connection Audit
```bash
./scripts/ntopng-helper.sh connections <ip> [sample_size]
```
Extracts a sample of external domains contacted by a specific device from ntopng logs.

### 4. Health & Statistics
```bash
./scripts/ntopng-helper.sh status   # Verifies the ntopng service state
./scripts/ntopng-helper.sh stats    # Global network device counts
```

## Data Interpretation Guide

*   **Exfiltration Pattern:** An Upload:Download ratio higher than 5:1 on a non-server device is a high-priority anomaly.
*   **Device Spoofing:** Unexpected MAC addresses or MACs with the `DE:AD:BE:EF` prefix (often VPN/Tunnel interfaces) should be verified.
*   **Protocol Anomalies:** Use the `app` command to detect devices using protocols that violate your local security policy (e.g., unexpected SSH or HTTP servers).

## Security Implementation

- **No Secret Leaking:** Scripts are hardened to never echo credentials or sensitive environment variables.
- **Input Sanitization:** Arguments are filtered to prevent shell injection attempts.
- **Secure by Default:** SSL verification is active unless explicitly overridden for lab use.
