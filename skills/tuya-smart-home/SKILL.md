---
name: tuya-smart-home
description: "Control Tuya/Smart Life smart home devices including pet feeders, lights, plugs, curtains via cloud API or local network. Use when: (1) controlling smart home devices, (2) feeding pets remotely, (3) managing Tuya/Smart Life devices, (4) scanning local Tuya devices, (5) querying device status like battery or temperature."
---

# Tuya Smart Home

Control any Tuya/Smart Life device via cloud API or local network.

## Dependencies

```bash
pip3 install tinytuya tuya-connector-python
```

## Configuration

Two control modes available:

### Cloud Mode
Requires Tuya IoT Platform credentials from https://iot.tuya.com:
- `ACCESS_ID` — from Cloud Project
- `ACCESS_SECRET` — from Cloud Project  
- `REGION` — cn (China), us (Americas/SEA), eu (Europe), in (India)

### Local Mode (Recommended)
Requires device info (obtain via cloud API first):
- `DEVICE_ID` — device identifier
- `LOCAL_KEY` — device encryption key
- `IP` — device local IP address
- `VERSION` — protocol version (usually 3.4)

## Quick Start

### Scan for devices on local network

```bash
python3 scripts/tuya_scan.py
```

### Get device info (cloud)

```bash
python3 scripts/tuya_control.py --mode cloud --action info \
  --device-id DEVICE_ID \
  --access-id ACCESS_ID --access-secret ACCESS_SECRET --region cn
```

### Query device status

```bash
# Cloud
python3 scripts/tuya_control.py --mode cloud --action status \
  --device-id DEVICE_ID \
  --access-id ACCESS_ID --access-secret ACCESS_SECRET --region cn

# Local
python3 scripts/tuya_control.py --mode local --action status \
  --device-id DEVICE_ID --ip IP --local-key KEY
```

### Send command

```bash
# Cloud — feed pet 1 portion
python3 scripts/tuya_control.py --mode cloud --action send \
  --device-id DEVICE_ID --code manual_feed --value 1 \
  --access-id ACCESS_ID --access-secret ACCESS_SECRET --region cn

# Local — feed pet 1 portion
python3 scripts/tuya_control.py --mode local --action send \
  --device-id DEVICE_ID --ip IP --local-key KEY \
  --dp-id 3 --value 1

# Turn on light
python3 scripts/tuya_control.py --mode cloud --action send \
  --device-id DEVICE_ID --code switch_led --value true \
  --access-id ACCESS_ID --access-secret ACCESS_SECRET --region cn

# Open curtain
python3 scripts/tuya_control.py --mode cloud --action send \
  --device-id DEVICE_ID --code control --value open \
  --access-id ACCESS_ID --access-secret ACCESS_SECRET --region cn
```

## Common Device Commands

| Device | Code | Values | Description |
|--------|------|--------|-------------|
| Pet Feeder | manual_feed | 1-12 | Feed N portions |
| Pet Feeder | quick_feed | true | Quick feed |
| Pet Feeder | light | true/false | Night light |
| Light | switch_led | true/false | On/off |
| Light | bright_value | 10-1000 | Brightness |
| Light | temp_value | 0-1000 | Color temperature |
| Plug | switch_1 | true/false | On/off |
| Curtain | control | open/stop/close | Movement |
| Curtain | percent_control | 0-100 | Position % |

## China Region Note

China data center (`openapi.tuyacn.com`) blocks non-China IPs by default.
**Solutions:**
1. Add your IP to whitelist in Tuya IoT Platform → Project → IP Whitelist
2. Use **local mode** (bypasses cloud entirely, recommended)

## API Reference

For detailed API documentation, DP code tables, and setup guide, see [references/tuya_api.md](references/tuya_api.md).
