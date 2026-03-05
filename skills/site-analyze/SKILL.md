---
name: site-analyze
description: 网站机房溯源全维度分析工具。当用户要求分析某个网站的机房位置、CDN、IP归属、路由链路、响应延迟、SSL证书、子域名等信息时使用。支持通过 DNS over HTTPS（阿里/腾讯/360）查询绕过UDP封锁，自动识别 Cloudflare、Akamai、阿里云、腾讯云等主流CDN，输出完整的溯源分析报告。
---

# Site Analyze — Website Infrastructure Tracer

Runs 9 analysis modules and prints a full infrastructure report for any domain.
No API keys required. Works from any network with outbound HTTPS access.

## Usage

```bash
python3 scripts/site-analyze.py <domain>
```

Accepts bare domains or full URLs (scheme/path stripped automatically):

```bash
python3 scripts/site-analyze.py example.com
python3 scripts/site-analyze.py https://example.com/some/path
```

## Analysis Modules

| # | Module | Method |
|---|--------|--------|
| 0 | DoH server probe | Auto-detects working DNS-over-HTTPS servers from 8 candidates |
| 1 | DNS resolution | Multi-server DoH (Google/CF/Quad9/AliDNS/DNSPod/360/AdGuard/OpenDNS) + A/AAAA/MX/NS/TXT/SOA |
| 2 | IP geolocation & CDN | ipinfo.io + built-in ASN→CDN database (Cloudflare, Akamai, Fastly, AWS, Aliyun, Tencent…) |
| 3 | Subdomain enumeration | Common subdomain DoH scan + crt.sh CT logs + HackerTarget; ⭐ flags non-CDN IPs |
| 4 | TCP latency | Python socket, 80+443, 3 samples each; warns when IP is anycast |
| 5 | HTTP/HTTPS headers | curl; extracts CF-RAY, server, x-powered-by, via, proxy-agent, x-cache… |
| 6 | HTTPS timing breakdown | curl: DNS / TCP / TLS / TTFB / total; estimates one-way RTT to edge |
| 7 | SSL certificate | openssl: issuer, subject, SAN, validity dates |
| 8 | TCP traceroute | tcptraceroute (fallback: ICMP traceroute) |
| 9 | Summary & verdict | Auto-flags discovered origin IPs; advises on CDN-hidden origins |

## Reading Results

- **TCP latency low but TTFB high** → target uses Anycast edge; real origin is farther away
- **`anycast: true`** on an IP → TCP latency reflects nearest PoP, not origin location; use TTFB
- **CF-RAY suffix** → Cloudflare PoP that handled the request (AMS = Amsterdam, SJC = San Jose…)
- **`proxy-agent: VM-xxx-centos`** in a 502 → origin server info leaked by Cloudflare error
- **⭐ subdomain** → resolves to a non-CDN IP; likely the real origin

## Dependencies

- Python 3.6+ (stdlib only)
- `curl` (headers + timing)
- `openssl` (SSL cert)
- `tcptraceroute` or `traceroute` (optional; traceroute step skipped if absent)
