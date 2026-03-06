# Changelog

All notable changes to the Strava OpenClaw skill will be documented in this file.

## [1.0.0] - 2026-02-12

### Added
- Initial release
- Query recent Strava activities
- View weekly/monthly running and cycling stats
- Check last workout details
- Interactive setup wizard for OAuth
- Sanitized credentials (no hardcoded API keys)
- Comprehensive documentation

### Features
- `strava_control.py recent` - Show recent activities
- `strava_control.py stats` - Show weekly/monthly stats
- `strava_control.py last` - Show last workout
- `setup.py` - Interactive OAuth setup

### Requirements
- Python 3.7+
- stravalib package
- Strava API credentials (free)
