# Advanced Kotlin

## Delegation

- `by lazy` is thread-safe by default (SYNCHRONIZED) — use `LazyThreadSafetyMode.NONE` if single-threaded
- `by Delegates.observable` for property change listeners — callback on every set
- `by Delegates.vetoable` can reject value changes — return false to keep old value
- `by map` for delegating to map entries — useful for config objects
- Custom delegates: implement `getValue`/`setValue` operators — reuse property patterns

## Inline Functions

- `inline` copies function body at call site — eliminates lambda allocation overhead
- `noinline` params not inlined, can be stored — needed if passing lambda to another function
- `crossinline` prevents non-local returns — use in lambdas passed to other contexts
- Don't inline large functions — increases bytecode size, hurts performance

## Reified Types

- `reified` only works in inline functions — type info preserved at runtime
- Use for `is` checks without passing `Class<T>` — `inline fun <reified T> isType(x: Any) = x is T`
- Can't use reified on non-inline — type erasure applies
- Common use: `Gson().fromJson<MyType>(json)` without class parameter

## Kotlin Multiplatform

- `expect`/`actual` for platform-specific code — expect in common, actual per platform
- Common code can't use platform APIs directly — abstract behind expect declarations
- `actual typealias` for simple platform mappings — when platform class matches expect
- Gradle source sets: commonMain, androidMain, iosMain — dependencies flow down
- Expect classes can have default implementations — actual only overrides what differs

## Contracts

- `contract { returns() implies (value != null) }` — smart cast after function call
- Only experimental in stdlib — but safe to use established ones
- `callsInPlace(EXACTLY_ONCE)` — enables initialization in lambdas for `run`, `let`, etc.
