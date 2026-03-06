# Feature Flags & Progressive Delivery

## Feature Flag Implementation

```typescript
// Simple feature flag service
const flags = new Map<string, boolean>()

export const featureFlags = {
  isEnabled(key: string): boolean {
    return flags.get(key) ?? false
  },
  
  enable(key: string) {
    flags.set(key, true)
  },
  
  disable(key: string) {
    flags.set(key, false)
  },
}

// Usage
if (featureFlags.isEnabled('new-checkout')) {
  return <NewCheckout />
}
return <OldCheckout />
```

## A/B Testing

```typescript
// Simple A/B bucket
function getBucket(userId: string, experiment: string): 'a' | 'b' {
  const hash = hash(`${userId}:${experiment}`)
  return hash % 2 === 0 ? 'a' : 'b'
}

// Usage
const bucket = getBucket(userId, 'checkout-button-color')
if (bucket === 'a') {
  return <Button color="blue" />
}
return <Button color="green" />
```

## Kill Switch

```typescript
// Emergency disable
app.get('/feature/:key', (req, res) => {
  if (req.query.disable === 'true') {
    featureFlags.disable(req.params.key)
    return res.json({ status: 'disabled' })
  }
  return res.json({ enabled: featureFlags.isEnabled(req.params.key) })
})
```

## Checklist

- [ ] Choose feature flag tool (LaunchDarkly, Unleash, custom)
- [ ] Implement flag evaluation
- [ ] Add user targeting
- [ ] Set up A/B experiments
- [ ] Create kill switches
- [ ] Plan rollout percentage
