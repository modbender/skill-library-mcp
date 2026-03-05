---
name: WiFi
description: Troubleshoot and secure wireless networks with channel optimization and diagnostics.
metadata: {"clawdbot":{"emoji":"📶","os":["linux","darwin","win32"]}}
---

## Band Selection Traps
- 2.4GHz penetrates walls better but congested — neighbors' networks interfere
- 5GHz faster but shorter range — may not reach all rooms
- Same SSID for both bands can cause issues — device may stick to weak 5GHz instead of switching
- 6GHz (WiFi 6E) requires compatible devices — falls back to 5GHz if unsupported

## Channel Interference
- 2.4GHz only has 3 non-overlapping channels (1, 6, 11) — using others causes interference with neighbors
- "Auto" channel selection often picks poorly — scan and set manually in congested areas
- 5GHz has more channels but DFS channels may pause for radar — causes brief disconnects near airports
- Microwave ovens interfere with 2.4GHz channel 11 — kitchen dead zones are real

## Security Mistakes
- WPA2-Personal minimum — WEP and WPA crackable in minutes
- WPA3 preferred when all devices support — falls back silently if mixed
- WPS is a backdoor — disable it, PIN can be brute-forced regardless of password strength
- Hidden SSID doesn't improve security — devices broadcast it anyway when searching
- MAC filtering trivially bypassed — MACs visible in air, easy to spoof

## Speed Issues
- "Connected" doesn't mean good signal — check RSSI, below -70dBm is poor
- WiFi speed is shared medium — many devices = less bandwidth each
- Advertised speeds are theoretical max — real throughput is 50-70% at best
- Old devices slow entire network on 2.4GHz — legacy rates affect everyone
- USB 3.0 devices interfere with 2.4GHz — especially external drives near router

## Connection Drops
- DHCP lease expiring causes reconnect — reduce lease time for troubleshooting, increase for stability
- Roaming between access points isn't seamless — same SSID doesn't mean smooth handoff
- Power saving mode causes ping spikes — disable on devices where latency matters
- Driver issues more common than hardware — update or rollback WiFi drivers first

## Diagnostics
- Ping router IP, not internet — isolates WiFi from ISP issues
- Signal strength varies by location — walk around while monitoring
- Channel scanner shows neighbor congestion — choose least crowded
- Packet loss under 1% is acceptable — higher indicates interference or range issues

## Router Placement
- Center of coverage area, not corner of house — signals radiate outward
- Elevated position improves coverage — floor level gets blocked by furniture
- Away from metal objects and aquariums — water and metal block signals
- Router antennas perpendicular to each other — covers horizontal and vertical planes

## Guest Networks
- Isolates untrusted devices from main network — IoT devices can't reach your computers
- Separate password allows sharing without exposing main credentials
- Bandwidth limiting available on most routers — prevent guests from saturating connection
- Captive portal unnecessary for home — just use WPA2 with password

## Mesh vs Extenders
- Extenders halve bandwidth — repeating uses same channel for backhaul
- Mesh systems with dedicated backhaul avoid this — wired backhaul even better
- Single router often enough — try repositioning before buying mesh
- Adding access points to wrong locations creates more problems — coverage overlap causes roaming issues
