# Collections & Data Classes

## Immutability

- `listOf` is immutable — use `mutableListOf` if you need to modify
- `map`, `filter`, `reduce` are lazy on Sequences — use `.asSequence()` for large chains

## Safe Access

- `first()` throws on empty — use `firstOrNull()` for safe access
- `associate` and `groupBy` replace manual map building — cleaner than forEach with mutableMap
- Destructuring: `for ((key, value) in map)` — also works with data classes

## Data Classes

- `data class` auto-generates `equals`, `hashCode`, `copy`, `toString` — don't write manually
- Only constructor properties in `equals`/`hashCode` — body properties ignored
- `copy()` for immutable updates — `user.copy(name = "New")` keeps other fields
- Prefer data classes for DTOs and state — but not for entities with identity beyond data
