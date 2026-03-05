name: pcap-analyzer
description: Analyze PCAP/PCAPNG files with tshark and produce a structured network-forensics summary (talkers, ports, DNS, TLS, HTTP, anomalies).
homepage: https://www.wireshark.org/docs/man-pages/tshark.html
metadata:
  {
    "openclaw":
      {
        "emoji": "🦈",
        "requires":
          {
            "bins": ["tshark", "awk", "sed"],
            "files": ["/home/tom/openclaw-tools/pcap_summary.sh"]
          },
        "notes":
          [
            "This skill runs local analysis only. It does not exfiltrate the PCAP.",
            "Prefer read-only access; do not modify user files."
          ]
      }
  }
---

# PCAP Analyzer (tshark)

This skill turns packet captures into a practical report a human can act on. It is designed for lab work, incident triage, and CPENT-style exercises.

## What it produces

A structured report with:

- **Capture metadata**: file type, size, first/last timestamp (if available)
- **Top talkers**: endpoints by packets/bytes (IPv4/IPv6 when present)
- **Conversations**: top TCP/UDP conversations
- **Service/port view**: top TCP/UDP destination ports
- **DNS**: most common queried names + suspicious patterns (DGA-ish, long labels)
- **TLS**: SNI / Server Name and common JA3-like fingerprints when present (best-effort)
- **HTTP**: host headers / URLs when present (best-effort, only if decrypted/plain)
- **Anomalies** (best-effort heuristics):
  - SYN-only scans / high SYN rate
  - excessive RSTs
  - retransmission bursts
  - rare destination ports
  - single host contacting many unique hosts (beaconing-like)

## Inputs

You must provide:

- `pcap_path`: Full path to a `.pcap` or `.pcapng` file **on this machine**.

Optional:
- `focus_host`: IP to focus on (filters summaries around that host)
- `time_window`: A display filter time window if user specifies (best-effort guidance only)

## How to run (terminal)

```bash
{baseDir}/scripts/analyze.sh "/full/path/to/capture.pcapng"

