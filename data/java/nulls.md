# Nulls, Optional & Autoboxing

## String Gotchas
- `==` compares references, not content — always use `.equals()` for strings
- String pool: literals interned, `new String()` not — `"a" == "a"` true, `new String("a") == "a"` false
- Strings are immutable — concatenation in loop creates garbage, use `StringBuilder`
- `null.equals(x)` throws NPE — use `"literal".equals(variable)` or `Objects.equals()`

## Null Handling
- NPE is most common exception — check nulls or use `Optional<T>`
- `Optional.get()` throws if empty — use `orElse()`, `orElseGet()`, or `ifPresent()`
- Don't use Optional for fields or parameters — intended for return types
- `@Nullable` and `@NonNull` annotations help static analysis — not enforced at runtime
- Primitive types can't be null — but wrappers (`Integer`) can, autoboxing hides this

## Autoboxing Dangers
- `Integer == Integer` uses reference for values outside -128 to 127 — use `.equals()`
- Unboxing null throws NPE — `Integer i = null; int x = i;` crashes
- Performance: boxing in tight loops creates garbage — use primitives
- `Integer.valueOf()` caches small values — `new Integer()` never caches (deprecated)
