# Kotlin Idioms

## Scope Functions

- `let` for null checks and transformations — `value?.let { use(it) }`
- `apply` for object configuration — `MyObject().apply { prop = value }` returns object
- `run` for scoped computation — `val result = obj.run { compute() }` returns result
- `also` for side effects — `value.also { log(it) }` returns original
- Don't nest scope functions — readability drops fast, extract to named functions

## Extension Functions

- Extend existing classes without inheritance — `fun String.isEmail(): Boolean`
- Keep extensions close to usage — don't scatter across codebase
- Extension on nullable: `fun String?.orEmpty()` — can be called on null
- Extensions are resolved statically — not polymorphic, receiver type matters at compile time

## Sealed Classes

- Exhaustive `when` — compiler ensures all subclasses handled
- Perfect for state machines and results — `sealed class Result<T> { Success, Error }`
- Subclasses must be in same file (or same package in Kotlin 1.5+) — intentional restriction
- `sealed interface` for multiple inheritance — when you need to implement other interfaces
