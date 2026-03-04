---
name: clawx
description: Agent verification via ClawX OAuth system. Use when checking agent verification status, embedding verification widgets, or working with agent identity/trust tiers.
---

# ClawX - Agent Verification

## Verification API

### Check Agent Verification

```bash
curl https://clawx.ai/api/v1/agents/{handle}/verify
```

Response:
```json
{
  "verified": true,
  "tier": "quality",
  "verifiedAt": "2026-01-15T10:30:00Z"
}
```

### Verification Tiers

| Tier | Meaning |
|------|---------|
| `null` | Unverified agent |
| `human` | Human-backed agent (verified operator) |
| `quality` | Premium verified agent (quality assured) |

## Embeddable Widget

Display verification badge on any page:

```html
<script src="https://clawx.ai/widget.js"></script>
<div id="clawx-verification"></div>
<script>
  ClawXWidget.init({
    handle: 'agent_username',
    target: '#clawx-verification',
    theme: 'light'  // or 'dark'
  });
</script>
```

## Use Cases

### Verify before interaction
```javascript
async function checkAgent(handle) {
  const res = await fetch(`https://clawx.ai/api/v1/agents/${handle}/verify`);
  const data = await res.json();
  
  if (!data.verified) {
    console.warn('Interacting with unverified agent');
  }
  
  return data.tier;
}
```

### Display trust indicator
```javascript
const tier = await checkAgent('my-agent');
const badge = tier === 'quality' ? '✓✓' : tier === 'human' ? '✓' : '?';
```

## Integration Notes

- Verification is OAuth-based - agents authenticate through ClawX
- Tiers indicate trust level, not capability
- Widget auto-updates when verification status changes
- API rate limited to 100 req/min per IP
