# Concurrency Traps

- `async let` starts immediately — not when you `await`
- Actor isolation: accessing actor property from outside requires `await` — even for reads
- `@MainActor` doesn't guarantee immediate main thread — it's queued
- `Task.detached` loses actor context — inherits nothing from caller
- Sendable conformance: mutable class properties violate thread safety silently until runtime crash

# Value vs Reference

- Structs copied on assign, classes shared — mutation affects only copy or all references
- Large structs copying is expensive — profile before assuming copy-on-write saves you
- Mutating struct in collection requires reassignment — `array[0].mutate()` doesn't work, extract, mutate, replace
- `inout` parameters: changes visible only after function returns — not during
