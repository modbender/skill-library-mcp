# Tech Security Audit Skill

This skill provides network vulnerability assessment capabilities through Nmap integration.

## Features

- Local network scanning
- Vulnerability detection
- Service version identification
- OS fingerprinting

## Requirements

- Nmap must be installed and accessible in PATH
- Python 3.6+
- Appropriate network permissions for scanning

## Installation

1. Install Nmap on your system
2. Ensure Nmap is in your system PATH
3. Verify installation with `nmap --version`

## Usage

```python
from tech_security_audit import run_nmap_scan

# Perform a vulnerability scan
results = run_nmap_scan("192.168.1.0/24", "vulnerability")

# Perform a service detection scan
results = run_nmap_scan("192.168.1.100", "service")

# Perform an OS detection scan
results = run_nmap_scan("192.168.1.100", "os")
```

## Scan Types

- **vulnerability**: Runs vulnerability detection scripts
- **service**: Detects services and their versions
- **os**: Performs OS fingerprinting

## Output Format

The scanner returns structured results including:
- Host information (IP, hostname, status)
- Services (port, protocol, state, service name, version)
- OS fingerprinting results
- Vulnerability findings

## Legal Notice

This tool is intended for authorized security testing only. Users are responsible for complying with all applicable laws and regulations.