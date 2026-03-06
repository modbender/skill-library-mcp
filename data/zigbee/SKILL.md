---
name: Zigbee
description: Deploy and troubleshoot Zigbee mesh networks for home automation.
metadata: {"clawdbot":{"emoji":"🐝","os":["linux","darwin","win32"]}}
---

## Mesh Network Traps
- Battery devices don't route — only mains-powered devices extend mesh
- Mesh needs routers every 10-15m — one coordinator alone has limited range
- Adding routers requires rebuilding routes — devices don't automatically find new paths
- First devices paired become mesh backbone — pair routers before sensors

## Coordinator Issues
- Only one coordinator per network — two coordinators create two separate networks
- Coordinator stick placement matters — USB extension away from computer reduces interference
- Coordinator migration loses all pairings — backup before switching hardware
- Some sticks need firmware flash — Sonoff, CC2531 don't work out of box

## WiFi Interference
- Zigbee shares 2.4GHz spectrum — WiFi channels overlap with Zigbee channels
- Zigbee channel 11 = WiFi channel 1, Zigbee 25 = WiFi 11 — pick non-overlapping
- Default Zigbee channel 11 often worst — conflicts with common WiFi defaults
- Changing Zigbee channel requires re-pairing all devices — choose carefully initially

## Compatibility Issues
- "Zigbee compatible" doesn't mean interoperable — some devices only work with their hub
- Xiaomi/Aqara devices drop off generic coordinators — need specific handling
- Tuya Zigbee often requires their gateway — may not pair with Zigbee2MQTT
- Check device compatibility list before buying — not all Zigbee is equal

## Pairing Problems
- Pairing mode timeout is short — be ready before enabling
- Factory reset required if previously paired — hold button 5-10 seconds
- Distance during pairing matters — pair close to coordinator, move after
- Some devices need multiple reset attempts — keep trying

## Groups vs Binding
- Groups: coordinator sends one command to all — requires coordinator online
- Binding: direct device-to-device — works without coordinator, lower latency
- Binding a switch to bulbs survives coordinator reboot — groups don't
- Not all devices support binding — check before planning automation

## Battery Devices
- Battery sensors sleep aggressively — commands only received on wake
- Check-in intervals vary by device — some wake every hour, others every few seconds
- Reporting thresholds affect battery life — frequent updates drain faster
- Replacing battery sometimes requires re-pairing — device forgets network

## Common Failures
- Device shows online but doesn't respond — try power cycle, check routing
- Intermittent responses — mesh too sparse, add routers
- Delayed commands — routing through many hops, add closer router
- New device won't pair — network in wrong mode, coordinator issue, or device not reset
