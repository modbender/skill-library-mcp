# Best Practices — WhatsApp Business API

## Message Timing

### 24-Hour Conversation Window

```
Customer sends message
        │
        ▼
┌───────────────────────┐
│  24-Hour Free Window  │  ← Reply freely (any message type)
│  (No template needed) │
└───────────────────────┘
        │
        ▼ (24h passed)
┌───────────────────────┐
│   Template Required   │  ← Must use approved template
│   (Costs per message) │
└───────────────────────┘
```

**Best Practice:** Respond within 24 hours to avoid template costs.

---

## Conversation Pricing

### Conversation Types

| Type | Who Initiates | Cost (approx) |
|------|---------------|---------------|
| Service | Customer | Lower |
| Utility | Business (order updates, etc.) | Medium |
| Authentication | Business (OTPs) | Medium |
| Marketing | Business (promos) | Higher |

### Free Entry Points

These conversations are free for 72 hours:
- Click-to-WhatsApp ads
- Facebook Page CTA button
- WhatsApp button on Instagram

---

## Rate Limits

### API Limits

| Limit | Value |
|-------|-------|
| Messages/second | 80 per phone number |
| API calls/second | 100 per app |
| Media upload/day | 500 per phone number |

### Messaging Limits

| Tier | Unique Users/Day |
|------|------------------|
| Unverified | 250 |
| Tier 1 | 1,000 |
| Tier 2 | 10,000 |
| Tier 3 | 100,000 |
| Tier 4 | Unlimited |

**Upgrade Path:** Maintain GREEN quality rating for 7 days → automatic upgrade.

---

## Quality Best Practices

### DO

✅ Respond quickly (within 24h)
✅ Use templates for important updates
✅ Personalize messages with user's name
✅ Provide clear opt-out instructions
✅ Send messages at reasonable hours
✅ Match message to user's language

### DON'T

❌ Send unsolicited marketing
❌ Spam with multiple messages
❌ Use URL shorteners (appears suspicious)
❌ Send same message to many users rapidly
❌ Ignore user replies
❌ Use misleading template content

---

## Template Best Practices

### Naming Convention

```
{purpose}_{version}
order_confirmation_v2
shipping_update_v1
appointment_reminder_v3
```

### Content Guidelines

1. **Be specific** — "Your order #{{1}} shipped" not "Your order shipped"
2. **Include context** — Why are you messaging?
3. **Add value** — Information they actually need
4. **Enable action** — Include relevant links/buttons
5. **Respect time** — Don't wake people up

### Approval Tips

- Use proper grammar and spelling
- Avoid ALL CAPS
- Don't use excessive emojis
- Include your business name
- Be transparent about intent

---

## Webhook Handling

### Recommended Architecture

```
Webhook Request
      │
      ▼
┌─────────────────┐
│  Validate       │  ← Check signature
│  Signature      │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Return 200     │  ← Immediately!
│  (sync)         │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Queue Message  │  ← Add to job queue
│  (async)        │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Process        │  ← Worker processes
│  (background)   │
└─────────────────┘
```

### Idempotency

```javascript
// Store processed message IDs
const processedIds = new Set();

function handleMessage(message) {
  if (processedIds.has(message.id)) {
    return; // Already processed
  }
  
  processedIds.add(message.id);
  // Process message...
}
```

---

## Error Handling

### Retry Strategy

```javascript
async function sendWithRetry(message, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await sendMessage(message);
    } catch (error) {
      if (error.code === 130429) { // Rate limited
        await sleep(Math.pow(2, i) * 1000); // Exponential backoff
        continue;
      }
      throw error; // Non-retryable
    }
  }
  throw new Error('Max retries exceeded');
}
```

### Error Categories

| Code Range | Type | Action |
|------------|------|--------|
| 131xxx | Message errors | Fix request |
| 132xxx | Template errors | Check template |
| 133xxx | Rate/limit errors | Slow down |
| 135xxx | Generic errors | Check docs |

---

## Security Checklist

- [ ] Store tokens in environment variables
- [ ] Verify webhook signatures
- [ ] Use HTTPS for all endpoints
- [ ] Implement rate limiting on your end
- [ ] Log API calls (without sensitive data)
- [ ] Rotate tokens periodically
- [ ] Monitor for unusual activity
- [ ] Have incident response plan

---

## Testing

### Test Numbers

Use Meta-provided test numbers in development:
1. Go to WhatsApp → API Setup in App Dashboard
2. Add test phone numbers
3. Use temporary access token

### Sandbox Limits

- 5 test phone numbers
- Templates work in sandbox
- No charges for test messages

### Pre-launch Checklist

- [ ] Templates approved
- [ ] Webhooks verified and handling all events
- [ ] Error handling tested
- [ ] Rate limiting implemented
- [ ] Quality rating monitored
- [ ] Opt-out flow working
- [ ] Business verification complete

---

## Monitoring

### Key Metrics

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Delivery rate | >95% | Check phone numbers |
| Read rate | >60% | Improve content |
| Response time | <1h | Add resources |
| Quality rating | GREEN | Review practices |
| Template approval | >80% | Improve content |

### Alerts to Set Up

1. Quality rating drops to YELLOW
2. Delivery rate below 90%
3. Webhook failures
4. Rate limit warnings
5. Template rejections
