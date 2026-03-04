# Ham Radio DX Monitor - Quick Start

Monitor DX clusters for rare station spots and get daily digests.

## Installation

No installation needed - this is an OpenClaw skill. Just load it and use.

## Manual Usage

```bash
# Watch latest spots
python3 dx-monitor.py watch --callsign YOUR_CALL

# Only NEW spots (filters duplicates)
python3 dx-monitor.py watch --new-only --callsign YOUR_CALL

# Daily digest
python3 dx-monitor.py digest --callsign YOUR_CALL
```

## Automated Monitoring

Use OpenClaw cron for automated monitoring:

```bash
# Add DX monitor job (every 5 minutes)
cron add --name "DX Watch" --schedule "*/5 * * * *" --sessionTarget main --payload 'systemEvent:Check DX cluster'
```

Or add to your crontab (as non-root user):

```bash
crontab -e
# Add: */5 * * * * /path/to/dx-monitor.py watch --new-only --callsign YOUR_CALL >> ~/dx.log 2>&1
```

## Configuration

Create a config file or pass arguments:

```bash
python3 dx-monitor.py watch --callsign KN4XYZ --cluster ea7jxh
```

## Output

The monitor outputs DX spots in readable format:

```
📡 Latest DX Spots from EA7JXH

   20m   SSB      14.195   K1ABC        - CQ Contest
   40m   CW        7.015   VP8/G3XYZ    - Falklands
```
