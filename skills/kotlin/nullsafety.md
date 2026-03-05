# Null Safety

## Operators

- `?.` safe call chains — `user?.address?.city` returns null if any is null
- `?:` Elvis for defaults — `name ?: "Unknown"` is cleaner than if-else
- `!!` asserts non-null — crashes on null, use only when you've already checked

## Patterns

- `let` for null-scoped operations — `user?.let { doSomething(it) }` only runs if non-null
- Combine with Elvis — `user?.name ?: return` for early exit

## Java Interop

- Platform types from Java are risky — add null checks or use `@Nullable`/`@NonNull` annotations
- Treat Java types as nullable by default — safer than assuming non-null
