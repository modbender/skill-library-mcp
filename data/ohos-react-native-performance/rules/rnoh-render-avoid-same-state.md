---
title: Avoid setState when state unchanged to prevent extra renders
impact: CRITICAL
source: ohos_react_native performance optimization - Application scenarios
---

# rnoh-render-avoid-same-state

Do not call setState when the new state equals the current state; otherwise React will still schedule a render (e.g. in the doc example, clicking when count is already 5 still triggers render).

## Incorrect

```javascript
increment = () => {
  const { count } = this.state;
  this.setState({ count: count + 1 }); // setState even when count is 5 → extra render
};
```

## Correct

```javascript
increment = () => {
  const { count } = this.state;
  const newCount = count < 5 ? count + 1 : count;
  if (newCount !== count) this.setState({ count: newCount });
};
// Or with functional update
increment = () => {
  this.setState(prev => {
    const next = prev.count < 5 ? prev.count + 1 : prev.count;
    return next === prev.count ? prev : { ...prev, count: next };
  });
};
```

## Note

- Static checks can flag event handlers that always call setState without "skip when value unchanged" logic for OpenHarmony React Native.
