# Foxcode Endpoints Reference

Complete reference for Foxcode AI service endpoints.

## Overview

Foxcode provides access to Claude Code models through multiple endpoints optimized for different use cases.

**Base Domain:** `code.newcli.com`
**Status Page:** https://status.rjj.cc/status/foxcode

---

## Endpoint Details

### 1. Official Dedicated Line (官方专用线路)

```
URL: https://code.newcli.com/claude
Status Monitor ID: 2
```

**Characteristics:**
- **Reliability:** Highest - primary production endpoint
- **Pricing:** Standard Foxcode rates
- **Speed:** Standard response times
- **Features:** Full Claude Code capabilities

**Best For:**
- Production workloads
- Users prioritizing reliability over cost
- First-time setup (recommended starting point)

**When to Use:**
- Daily development work
- Important tasks requiring consistency
- Learning and experimentation

---

### 2. Super Discount Line (Super特价线路)

```
URL: https://code.newcli.com/claude/super
Status Monitor ID: 5
```

**Characteristics:**
- **Reliability:** High - secondary production endpoint
- **Pricing:** Discounted rates (typically 20-30% savings)
- **Speed:** Good response times
- **Features:** Full Claude Code capabilities

**Best For:**
- Cost-conscious users
- High-volume usage
- Non-critical tasks

**When to Use:**
- Routine coding tasks
- Code reviews and explanations
- Documentation generation
- When Official endpoint shows issues

---

### 3. Ultra Discount Line (Ultra特价线路)

```
URL: https://code.newcli.com/claude/ultra
Status Monitor ID: 6
```

**Characteristics:**
- **Reliability:** Good - optimized for cost
- **Pricing:** Lowest rates (typically 40-50% savings)
- **Speed:** May have slightly higher latency
- **Features:** Full capabilities with possible rate limits

**Best For:**
- Maximum cost savings
- Batch processing jobs
- Background tasks

**When to Use:**
- Processing large volumes of requests
- Non-urgent tasks
- When cost is primary concern

**Considerations:**
- May have rate limits during peak hours
- Slightly higher latency acceptable for savings

---

### 4. AWS Discount Line (AWS特价线路)

```
URL: https://code.newcli.com/claude/aws
Status Monitor ID: 3
```

**Characteristics:**
- **Reliability:** High - AWS infrastructure
- **Pricing:** Standard rates
- **Speed:** Fastest response times
- **Features:** Full capabilities on AWS infrastructure

**Best For:**
- Speed-critical applications
- AWS ecosystem users
- Low-latency requirements

**When to Use:**
- Interactive coding sessions
- Real-time assistance
- When speed is primary concern

---

### 5. AWS Discount Line (Thinking) (AWS特价线路 - 思考)

```
URL: https://code.newcli.com/claude/droid
Status Monitor ID: 4
```

**Characteristics:**
- **Reliability:** High - AWS infrastructure with extended thinking
- **Pricing:** Standard rates
- **Speed:** Variable (longer for complex reasoning)
- **Features:** Extended thinking capability for complex tasks

**Best For:**
- Complex reasoning tasks
- Algorithm design
- Architecture decisions
- Multi-step problem solving

**When to Use:**
- Complex coding problems
- System design discussions
- Debugging intricate issues
- Research and analysis tasks

---

## Endpoint Selection Matrix

| Priority | Recommended Endpoint | Rationale |
|----------|---------------------|-----------|
| **Reliability** | Official | Primary production endpoint |
| **Cost** | Ultra | Lowest pricing tier |
| **Speed** | AWS | Fastest response times |
| **Complex Tasks** | AWS (Thinking) | Extended reasoning capability |
| **Balanced** | Super | Good cost/performance ratio |

## Quick Decision Flow

```
What's most important?
├── Reliability above all → Official
├── Maximum cost savings → Ultra
├── Fastest responses → AWS
├── Complex reasoning → AWS (Thinking)
└── Balanced approach → Super
```

## Monitoring and Status

### Real-time Status

Check current endpoint health:
```bash
python3 scripts/check_status.py
```

### Status Page

Web interface: https://status.rjj.cc/status/foxcode

**Monitored Metrics:**
- Response time (HTTP latency)
- Availability (uptime percentage)
- Incident history
- Geographic performance

### Fallback Strategy

If your primary endpoint is down:

1. Check status page for alternatives
2. Switch to Official endpoint (highest reliability)
3. Use Super endpoint as cost-effective backup
4. AWS endpoints for speed-critical fallback

## API Authentication

All endpoints use the same authentication method:

```
Header: Authorization: Bearer YOUR_API_TOKEN
Or Environment: FOXCODE_API_TOKEN=your_token
```

**Token Format:** `sk-foxcode-...`

**Get Token:** https://foxcode.rjj.cc/api-keys

## Request Format

Standard OpenAI-compatible request format:

```json
{
  "model": "claude-sonnet-4-5-20251101",
  "messages": [
    {"role": "user", "content": "Your prompt here"}
  ],
  "max_tokens": 4096
}
```

## Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request processed |
| 401 | Unauthorized | Check API token |
| 429 | Rate Limited | Wait and retry, or switch endpoint |
| 500 | Server Error | Try fallback endpoint |
| 503 | Service Unavailable | Check status page |

## Rate Limits

Rate limits vary by endpoint tier:

| Endpoint | Typical Limit | Burst Limit |
|----------|---------------|-------------|
| Official | 60/min | 120/min |
| Super | 60/min | 100/min |
| Ultra | 30/min | 60/min |
| AWS | 60/min | 120/min |
| AWS Thinking | 30/min | 60/min |

> Note: Actual limits may vary. Check your account dashboard for current limits.

## Geographic Considerations

Endpoints are distributed across regions:

- **Official/Super/Ultra:** Multi-region with automatic routing
- **AWS/AWS Thinking:** AWS global infrastructure

For optimal performance, choose the endpoint with lowest latency to your location.

## Migration Between Endpoints

To switch endpoints:

1. Update `base_url` in config
2. Restart OpenClaw
3. Test with simple prompt
4. Monitor for any issues

**Config Example:**
```json
{
  "base_url": "https://code.newcli.com/claude/super",
  "api_key": "sk-foxcode-...",
  "model": "claude-sonnet-4-5-20251101"
}
```

## Cost Optimization Tips

1. **Use Ultra for batch jobs** - 40-50% savings on non-urgent tasks
2. **Use Super for daily work** - 20-30% savings with good reliability
3. **Reserve Official for critical tasks** - Full reliability when needed
4. **Monitor usage** - Check dashboard regularly
5. **Set up alerts** - Get notified of unusual spending

## Support and Resources

- **Status Page:** https://status.rjj.cc/status/foxcode
- **API Keys:** https://foxcode.rjj.cc/api-keys
- **Setup Guide:** See README.md in this skill
- **Configuration:** See `references/openclaw-config.md`
