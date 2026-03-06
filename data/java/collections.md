# Collections & Iteration

## Equality Contract
- Override `equals()` must also override `hashCode()` — HashMap/HashSet break otherwise
- `equals()` must be symmetric, transitive, consistent — `a.equals(b)` implies `b.equals(a)`
- Use `getClass()` check, not `instanceof` — unless explicitly designed for inheritance
- `hashCode()` must return same value for equal objects — unequal objects can share hash
- Arrays: `Arrays.equals()` for content — `array.equals(other)` uses reference comparison

## Collections Pitfalls
- Modifying while iterating throws `ConcurrentModificationException` — use Iterator.remove() or copy
- `Arrays.asList()` returns fixed-size list — can't add/remove, backed by array
- `List.of()`, `Set.of()` return immutable — throw on modification attempts
- `HashMap` allows null key and values — `Hashtable` and `ConcurrentHashMap` don't
- Sort requires `Comparable` or `Comparator` — ClassCastException if missing
