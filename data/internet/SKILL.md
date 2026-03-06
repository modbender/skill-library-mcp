---
name: Internet
slug: internet
version: 1.0.0
description: Manage internet connectivity, compare providers, diagnose issues, optimize performance, and handle mobile data when away from home.
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with internet connectivity: comparing/switching providers, diagnosing speed issues, managing mobile data abroad, optimizing for gaming/streaming, or troubleshooting connection problems.

## Quick Reference

| Topic | File |
|-------|------|
| Provider comparison | `providers.md` |
| Diagnostics | `diagnostics.md` |
| Mobile connectivity | `mobile.md` |
| Performance optimization | `performance.md` |

## Core Rules

### 1. Diagnose Before Recommending
Run diagnostics first — don't assume the problem. Check:
- Speedtest vs contracted speed (flag if <70%)
- Packet loss and jitter
- DNS resolution time
- Whether issue is local, ISP, or destination

### 2. Provider Comparison Must Include Hidden Costs
When comparing providers:
- Show price AFTER promotional period ends
- Include early termination penalties
- Calculate total 24-month cost, not monthly
- Check coverage at user's exact address first

### 3. Mobile Data: Verify Before Activating
Before recommending eSIM/roaming:
- Confirm device eSIM compatibility
- Check destination country coverage
- Compare local SIM vs international eSIM vs roaming
- Alert user to data caps and throttling thresholds

### 4. Performance Claims Need Verification
For gaming/streaming optimization:
- Measure actual latency to game servers, not generic ping
- QoS changes require router admin access
- Bufferbloat is real — test with loaded connection
- "Faster DNS" rarely matters for speed, only for reliability

### 5. Keep History for ISP Disputes
Log incidents with timestamps:
- Date, time, duration of outages
- Speedtest results during issues
- Steps already attempted
- This evidence helps when escalating to ISP

## Common Traps

- Recommending provider switch without checking contract end date → user pays penalty
- Assuming WiFi issue when it's ISP problem → wasted troubleshooting
- eSIM purchase without verifying phone support → money lost
- QoS advice without knowing router model → unusable instructions
- Comparing speeds without noting technology (fiber vs cable vs DSL) → misleading

## Scope

This skill handles:
- ISP selection, comparison, and contract analysis
- Connection diagnostics and troubleshooting
- Mobile data management (eSIM, roaming, tethering)
- Performance optimization for specific use cases

This skill does NOT handle:
- WiFi-specific issues (channel optimization, security) → use `wifi` skill
- Network infrastructure setup (routers, mesh systems)
- VPN configuration or privacy tools
