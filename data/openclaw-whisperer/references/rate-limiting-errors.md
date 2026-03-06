# Rate Limiting Errors

Guide to managing API rate limits, quotas, and throttling in OpenClaw.

## Error Types

### 429 Too Many Requests

**Symptoms:**
- HTTP 429 status code from AI provider
- "Rate limit exceeded" error messages
- Requests temporarily rejected
- Slow or failed responses

**Common Causes:**
- Exceeding provider's requests-per-minute (RPM) limit
- Exceeding tokens-per-minute (TPM) limit
- Too many concurrent requests
- Shared API key hitting aggregate limits

**Provider Limits:**
```
OpenAI (Free Tier):
- 3 RPM, 40,000 TPM (GPT-3.5)
- 3 RPM, 150,000 TPM (GPT-4)

OpenAI (Pay-as-you-go):
- 3,500 RPM, 90,000 TPM (GPT-3.5)
- 500 RPM, 30,000 TPM (GPT-4)

Anthropic (Free Tier):
- 5 RPM, 25,000 TPM

Anthropic (Pro):
- 1,000 RPM, 100,000 TPM

Google Gemini (Free):
- 15 RPM, 1M TPM

Google Gemini (Pro):
- 360 RPM, 4M TPM
```

**Diagnostic Commands:**
```bash
# Check current rate limit status
openclaw status --rate-limits

# View request history
openclaw logs --filter="429" --last=1h

# Show quota usage
openclaw quota show
```

**Fix with Retry Strategy:**
```bash
# Enable exponential backoff in config
openclaw config set ai.retryStrategy.enabled true
openclaw config set ai.retryStrategy.maxRetries 3
openclaw config set ai.retryStrategy.backoffMs 1000

# Set rate limit buffer
openclaw config set ai.rateLimiting.bufferPercent 20
```

**Manual Fix:**
```bash
# Wait for rate limit window to reset (usually 1 minute)
sleep 60

# Reduce concurrent requests
openclaw config set ai.concurrency.max 2

# Enable request queuing
openclaw config set ai.queueing.enabled true
```

**Auto-Fix Available:** No (requires waiting or config adjustment)

---

### QUOTA_EXCEEDED

**Symptoms:**
- "Quota exceeded" error
- All requests fail even after waiting
- Provider dashboard shows 100% usage
- Billing alerts received

**Common Causes:**
- Monthly quota exhausted
- Free tier limit reached
- Billing issue (payment failed)
- Trial period expired

**Diagnostic Commands:**
```bash
# Check quota status
openclaw quota status --provider openai

# View usage breakdown
openclaw quota breakdown --last-30-days

# Estimate remaining capacity
openclaw quota estimate
```

**Fix:**
```bash
# Option 1: Upgrade tier
# Visit provider dashboard and upgrade plan

# Option 2: Switch to fallback provider
openclaw config set ai.fallback.enabled true
openclaw config set ai.fallback.provider anthropic

# Option 3: Wait for quota reset
# Monthly quotas reset on billing cycle date

# Option 4: Add additional API key
openclaw config set ai.openai.apiKeys '["sk-key1", "sk-key2"]'
openclaw config set ai.keyRotation.enabled true
```

**Prevention:**
```bash
# Set quota alerts
openclaw config set ai.quotaAlerts.enabled true
openclaw config set ai.quotaAlerts.thresholds '[80, 90, 95]'

# Enable cost tracking
openclaw config set ai.costTracking.enabled true
openclaw config set ai.costTracking.maxDailyCost 10.00
```

**Auto-Fix Available:** No (requires billing action)

---

### PROVIDER_THROTTLE

**Symptoms:**
- Intermittent slowdowns
- Requests succeed but take longer
- Provider returns "throttling" messages
- Degraded service notices

**Common Causes:**
- Provider-side load balancing
- Regional capacity limits
- Account-level throttling
- Abuse detection false positive

**Diagnostic Commands:**
```bash
# Check provider status
openclaw status --provider-health

# Measure response times
openclaw benchmark --provider openai --samples 10

# View throttling events
openclaw logs --filter="throttle" --last=24h
```

**Fix:**
```bash
# Reduce request frequency
openclaw config set ai.rateLimiting.requestsPerMinute 30

# Add request delays
openclaw config set ai.rateLimiting.minDelayMs 100

# Use different region endpoint
openclaw config set ai.openai.endpoint "https://api.openai.com/v1"  # Try different region

# Spread load across time
openclaw config set ai.scheduling.spreadLoad true
```

**Auto-Fix Available:** No (provider-side issue)

---

### CONCURRENT_LIMIT

**Symptoms:**
- "Too many concurrent requests" error
- Some requests queued indefinitely
- Gateway connection pool exhausted

**Common Causes:**
- Exceeding max concurrent connections (usually 100)
- Long-running requests blocking pool
- No connection timeout set
- WebSocket connections not closing

**Diagnostic Commands:**
```bash
# Check active connections
openclaw status --connections

# View connection pool stats
openclaw debug --connection-pool

# List long-running requests
openclaw requests --status running --min-duration 30s
```

**Fix:**
```bash
# Reduce max concurrent
openclaw config set ai.concurrency.max 50

# Set request timeout
openclaw config set ai.timeout.requestMs 30000

# Enable connection reuse
openclaw config set ai.http.keepAlive true
openclaw config set ai.http.maxSockets 100

# Clear stuck connections
openclaw connections reset
```

**Auto-Fix Available:** Yes

---

### BURST_LIMIT

**Symptoms:**
- Rapid succession of requests fails
- First few requests succeed, rest fail
- "Burst limit exceeded" message
- Short-term rate limit hit

**Common Causes:**
- Too many requests in short window (e.g., 10 requests in 1 second)
- Webhook spam
- Batch processing without delays
- Message flood from channel

**Diagnostic Commands:**
```bash
# View request burst patterns
openclaw analytics --metric burst --window 1s

# Check webhook activity
openclaw webhooks stats --last 5m
```

**Fix:**
```bash
# Enable burst protection
openclaw config set ai.burstProtection.enabled true
openclaw config set ai.burstProtection.maxPerSecond 5

# Add inter-request delays
openclaw config set ai.rateLimiting.burstDelayMs 200

# Implement message queuing
openclaw config set channels.queueing.enabled true
openclaw config set channels.queueing.maxPerSecond 3
```

**Auto-Fix Available:** No (requires config tuning)

---

## Rate Limiting Best Practices

### Configuration Template
```yaml
ai:
  rateLimiting:
    enabled: true
    requestsPerMinute: 50
    tokensPerMinute: 80000
    bufferPercent: 20
    minDelayMs: 100

  retryStrategy:
    enabled: true
    maxRetries: 3
    backoffMs: 1000
    backoffMultiplier: 2
    jitter: true

  concurrency:
    max: 10
    perProvider: 5

  queueing:
    enabled: true
    maxQueueSize: 100
    priorityMode: "fifo"

  fallback:
    enabled: true
    providers: ["anthropic", "google"]
    switchOnQuota: true
```

### Monitoring Strategy
```bash
# Real-time monitoring
openclaw status --watch --interval 5

# Daily quota summary
openclaw quota summary --email daily

# Alert on threshold
openclaw alerts add --metric quota --threshold 80 --action notify
```

### Cost Management
```bash
# Set daily budget
openclaw config set ai.budget.daily 20.00

# Enable cost alerts
openclaw config set ai.costAlerts.enabled true

# Track per-channel costs
openclaw analytics --metric cost --group-by channel
```

## Retry Strategies

**Exponential Backoff:**
- Retry after 1s, 2s, 4s, 8s...
- Prevents thundering herd
- Recommended for 429 errors

**Jittered Backoff:**
- Add random delay (±25%)
- Spreads load
- Best for multiple clients

**Fixed Delay:**
- Constant delay between retries
- Simple, predictable
- Use for non-critical requests

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Diagnostic Commands](diagnostic-commands.md) - CLI reference
- [Configuration Errors](configuration-errors.md) - Config issues
