# Performance Optimization — Internet

## Gaming Optimization

### What Actually Helps
- **Wired connection** — Always better than WiFi for latency
- **QoS prioritization** — If router supports, prioritize gaming traffic
- **Closer game servers** — Pick nearest region in game settings
- **Reduce network contention** — Pause other downloads during gaming

### What Rarely Helps
- "Gaming DNS" — DNS only affects initial connection, not gameplay
- "Gaming routers" — Marketing mostly, unless you need advanced QoS
- ISP "gaming packages" — Usually same infrastructure, different price

### Measuring Gaming Performance
```bash
# Ping to game servers (examples)
ping -c 20 riot.com           # League of Legends
ping -c 20 valve.net          # Steam/Dota/CS

# Check for packet loss and jitter, not just ping
# Good gaming: <50ms ping, 0% loss, <10ms jitter
```

## Streaming Optimization

| Quality | Required Speed | Recommended |
|---------|----------------|-------------|
| SD (480p) | 3 Mbps | 5 Mbps |
| HD (720p) | 5 Mbps | 10 Mbps |
| Full HD (1080p) | 10 Mbps | 25 Mbps |
| 4K | 25 Mbps | 50 Mbps |

If buffering despite good speed:
1. Test at different times (peak hours = congestion)
2. Try wired connection
3. Check if ISP throttles specific services
4. Clear streaming app cache

## Video Calls Optimization

For stable video calls:
- Upload speed matters more than download
- Need 3-5 Mbps upload for HD video
- Close other apps using network
- Use ethernet if possible
- Reduce video quality if unstable

## QoS Configuration

Most modern routers support QoS. General approach:
1. Access router admin (usually 192.168.1.1)
2. Find QoS or Traffic Management section
3. Enable and set priorities:
   - Highest: Video calls, gaming
   - High: Streaming
   - Normal: Web browsing
   - Low: Downloads, backups

Note: Specific steps vary by router model.

## Bufferbloat

**What it is:** Excessive buffering in network equipment causing latency spikes under load.

**Test for it:** Run speedtest while streaming — if ping spikes dramatically, you have bufferbloat.

**Solutions:**
- Enable SQM (Smart Queue Management) if router supports
- Reduce buffer sizes in router (advanced)
- Some routers have "anti-bufferbloat" settings
