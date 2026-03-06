# Error Handling Traps

- `fmt.Errorf("x: %w", err)` wraps — `%v` loses the chain
- `errors.Is(err, target)` checks chain — `==` only exact match
- `errors.As(err, &target)` extracts — pointer to pointer required
- Sentinel `errors.New()` called each time = new instance — define once as `var`
- Sentinel compared with `==` fails if wrapped — use `errors.Is`
- `if err != nil { return err }` loses context — wrap with `%w`
- `val, err := f()` — `val` may be valid even when `err != nil`
- Panic in goroutine crashes program — recover only in same goroutine
- `recover()` only in deferred function — not regular call
- Panic for bugs, error for expected — don't panic on user input
- Error type should be `*MyError` not `MyError` — pointer receiver
- `Unwrap()` enables `errors.Is/As` — forget and chain breaks
- Returning `(*MyError)(nil)` returns non-nil interface — nil trap
- `log.Fatal` calls `os.Exit(1)` — defers don't run
