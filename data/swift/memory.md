# Memory Leaks

- Closures capturing `self` strongly create retain cycles — use `[weak self]` in escaping closures
- Delegates must be `weak` — strong delegate = object never deallocates
- Timer retains target strongly — invalidate in `deinit` won't work, use `weak` or `block` API
- NotificationCenter observers retained until removed — remove in `deinit` or use `addObserver(forName:using:)` with token
- Nested closures: each level needs own `[weak self]` — inner closure captures outer's strong ref
