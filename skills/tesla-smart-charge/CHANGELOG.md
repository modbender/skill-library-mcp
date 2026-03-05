# Changelog

## [1.0.0] - 2026-02-02

### Features
- **Automatic charge scheduling** - Schedule Tesla charges on specific dates with target battery % and time
- **Intelligent start time calculation** - Automatically calculates optimal charging start time based on current battery level and charger power
- **Charge limit management** - Automatically manages charge limits during sessions (default 100%) and after sessions (default 80%) for battery health
- **Session state tracking** - Tracks active charging sessions and applies appropriate limits
- **Multi-vehicle support** - Configure via TESLA_EMAIL environment variable
- **Schedule-based automation** - JSON schedule file for flexible, date-based charging plans
- **Customizable charger power** - Support for different charger configurations (13A, 16A, 32A, etc.)

### Commands
- `--check-schedule` - Check if charge is scheduled for today and execute it
- `--manage-session` - Monitor active sessions and apply appropriate charge limits
- `--show-schedule` - Display all scheduled charges
- `--show-plan` - Show the last generated charging plan

### Configuration
- Supports charge limits during session (customizable per charge)
- Supports post-charge limits when session ends (customizable per charge)
- Default behavior: 100% during session, 80% after session for optimal battery health

### Documentation
- Complete SKILL.md with usage examples
- README.txt with quick start guide
- Example schedule JSON with new limit fields
- Recommended cron setup (daily check + session management)
