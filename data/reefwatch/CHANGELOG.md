# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2025-02-22

### Added
- Modular Python package with 12 modules (collectors, engines, alert manager)
- **Collectors**: log (syslog + journald), file watcher (SHA256 integrity), process monitor, network monitor (IOC IPs + domains)
- **Engines**: YARA (realtime + scheduled), Sigma (recursive-descent condition parser), custom JSON rules
- **Alert Manager**: severity filtering, deduplication, batching, JSONL history with rotation
- OpenClaw integrity checking with Unicode-aware prompt poisoning detection
- Config validation at startup
- Health/status JSON file (`/tmp/reefwatch_status.json`)
- FileWatcher directory mtime caching optimization
- Anti-SSRF webhook URL validation
- systemd and launchd service files
- Manual scan tool with JSON output (`manual_scan.py --json`)
- 130 unit tests with full coverage of all components
