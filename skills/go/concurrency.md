# Concurrency Traps

- Goroutine sin exit condition = forever — usar `ctx.Done()` o channel close
- `go func()` captura por referencia — loop variable trap: `go func(i int)` no `go func()`
- No way to kill goroutine from outside — must cooperate via context/channel
- Unbuffered channel = sync point — sender waits for receiver
- Buffer size 1 ≠ async — still blocks when full
- `select` multiple ready = random — not first listed
- Empty `select{}` blocks forever — useful for blocking main
- `default` makes select non-blocking — careful with busy loops
- Nil channel in select ignored — useful for disabling cases
- `defer mu.Unlock()` right after `Lock()` — don't do work between
- Lock/unlock in same function — avoid passing locked mutex
- Copying struct with mutex copies unlocked — always pass pointer
- `atomic.Value` Store must be same type — panics otherwise
- Atomic read + atomic write ≠ atomic read-modify-write — use `AddInt64`
- `context.TODO()` in prod = no cancellation — replace before shipping
- Context values wrong type = silent nil — use typed keys
