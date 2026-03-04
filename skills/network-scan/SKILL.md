# network-scan

## Description

This skill scans ports and devices on a network using nmap. It supports various target formats, including CIDR notation, IP ranges, and comma-separated lists.  Defaults to quick scan for CIDR.

## Inputs

*   `target`: The target network or IP address to scan (e.g., 192.168.1.0/24, 192.168.1.1-192.168.1.10, 192.168.1.1,192.168.1.2).
*   `ports`: The ports to scan (e.g., 80,443).
*   `--quick`: (Optional) Scan only the top 10 ports.
*   `--fast`: (Optional) Use aggressive scan settings (nmap -T4).
*   `--timeout`: (Optional) Set a timeout in seconds for the scan (default: 30).
*   `--top-ports`: (Optional) Scan the top N most common ports (e.g., --top-ports 100).
*   `--hosts-limit`: (Optional) Limit the number of hosts to scan (e.g., --hosts-limit 50).
*   `--exclude`: (Optional) Exclude a specific IP address from the scan (e.g., --exclude 192.168.1.5).

## Outputs

JSON object containing the nmap scan results. Includes scan results, nmap command used, and scan information.

## Usage

To use this skill, call it with the `target` and `ports` parameters:

```
network-scan target=192.168.1.0/24 ports=80,443 --fast --timeout 60 --hosts-limit 50 --exclude 192.168.1.100
```
