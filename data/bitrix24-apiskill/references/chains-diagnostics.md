# Chains: diagnostics

## 1) Method compatibility check

1. `method.get` with target method name.
2. If unavailable, call `scope` and compare with required scopes.
3. Use `methods` to inspect environment-specific method surface.

## 2) Event capability check

1. `feature.get` to verify offline-events support in current context.
2. `events` to fetch currently available events.
3. Continue with `event.bind` only when event appears in catalog and scope is valid.

## 3) Runtime sanity check

1. `server.time` to validate endpoint latency and clock response.
2. `user.current` from `core` pack to validate auth context.
