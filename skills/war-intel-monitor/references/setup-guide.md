# Quick Setup Guide

## Step 1: Copy Config Template

Copy `config-template.json` to your workspace as `war-intel-config.json`:

```bash
cp skills/war-intel-monitor/references/config-template.json ./war-intel-config.json
```

## Step 2: Configure Your Location

Edit `war-intel-config.json`:

1. **user_location**: Your home address, coordinates, and nearest shelters
2. **evacuation_target**: Where you want to evacuate to
3. **known_targets**: Military bases, airports, ports near you with distances
4. **emergency_contacts**: Local emergency numbers and embassy

### Finding Coordinates

Use Google Maps:
1. Right-click your location
2. Click the coordinates to copy
3. Format: [latitude, longitude]

### Calculating Distances

Use Google Maps "Measure distance" feature:
1. Right-click starting point → "Measure distance"
2. Click on target location
3. Distance shown in km

## Step 3: Set Up Monitoring

Ask the agent to create cron jobs:

```
Set up war intel monitoring for me:
- Read my config from war-intel-config.json
- Create urgent monitoring cron (every 30 min)
- Create daily briefing cron (3x daily at 8am, 2pm, 8pm)
- Send alerts to [Discord/Telegram/etc.]
```

## Step 4: Test

Ask for a manual briefing:

```
Generate a war intel briefing for my location based on war-intel-config.json
```

## Adjusting Alert Frequency

During active conflict: Keep 30-min monitoring
During low tension: Reduce to every 2-4 hours

```
Update my war intel monitoring to every 2 hours instead of 30 minutes
```
