# Diagnostics — Internet

## Quick Diagnosis Flow

```
1. Is it YOUR connection or THE SERVICE?
   → Test multiple sites/services
   → Check DownDetector for ISP outages

2. Is it WiFi or the actual internet?
   → Test wired connection if possible
   → If wired works fine → WiFi issue (use wifi skill)

3. Is it your network or the ISP?
   → Restart modem/router
   → Check modem lights for sync issues
   → If persists after restart → likely ISP

4. Is it speed or stability?
   → Speedtest for bandwidth
   → Ping test for packet loss/jitter
```

## Diagnostic Commands

```bash
# Basic connectivity
ping -c 10 8.8.8.8          # Packet loss to Google DNS
ping -c 10 1.1.1.1          # Packet loss to Cloudflare

# DNS resolution
nslookup google.com         # Should resolve quickly
dig google.com +stats       # Shows query time

# Traceroute (find where slowdown occurs)
traceroute 8.8.8.8          # macOS/Linux
tracert 8.8.8.8             # Windows

# Speedtest CLI
speedtest-cli               # If installed
curl -s https://fast.com    # Netflix speed test
```

## Interpreting Results

| Metric | Good | Concerning | Bad |
|--------|------|------------|-----|
| **Packet loss** | 0% | 1-2% | >3% |
| **Ping** | <30ms | 30-100ms | >100ms |
| **Jitter** | <5ms | 5-20ms | >20ms |
| **Speed vs contract** | >80% | 50-80% | <50% |

## When to Blame ISP

ISP is likely the problem if:
- Wired connection has same issues as WiFi
- Multiple devices affected simultaneously
- Issues persist after modem restart
- Traceroute shows high latency at ISP hops
- DownDetector shows reports in your area

## Documenting for ISP Support

When contacting ISP, have ready:
1. Account number
2. Exact times of issues (with timezone)
3. Speedtest results (screenshot with timestamp)
4. Steps already tried (modem restart, etc.)
5. Impact ("work from home, losing productivity")
