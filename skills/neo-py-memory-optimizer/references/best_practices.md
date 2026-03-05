# Python Memory Optimization Best Practices

## General Principles

1. **Prefer generators over lists** when you only need to iterate once.
2. **Use context managers** for any resource that needs cleanup (files, sockets, locks).
3. **Avoid mutable default arguments** — use `None` and create inside the function.
4. **Bound your caches** — use `functools.lru_cache(maxsize=N)` or similar bounded structures.
5. **Use `__slots__`** on data classes with many instances to reduce per-object overhead.
6. **Delete large temporary objects** with `del` when they are no longer needed.
7. **Use `array` or `numpy` arrays** for large homogeneous numeric data instead of Python lists.

## Data Structure Choices

| Need | Bad choice | Better choice | Memory savings |
|------|-----------|---------------|----------------|
| Iterate once | `list(...)` | Generator expression | ~100% of list size |
| Count occurrences | `dict` manually | `collections.Counter` | Marginal, but cleaner |
| Fixed-schema records | `dict` | `namedtuple` or `dataclass(slots=True)` | ~40-60% per instance |
| Large numeric arrays | `list` of `float` | `array.array('d', ...)` | ~4x reduction |
| Membership testing | `list` | `set` or `frozenset` | O(1) lookups, less iteration overhead |
| FIFO queue | `list` with `.pop(0)` | `collections.deque` | O(1) popleft vs O(n) |

## Common Pitfalls

### Circular References
Python's garbage collector handles most cycles, but classes with `__del__` methods
that participate in cycles can prevent collection. Use `weakref` to break cycles.

### Large String Building
Never concatenate strings in a loop with `+=`. Use `str.join()` or `io.StringIO`.

### Holding References Longer Than Needed
Closures and default arguments can capture references to large objects. Be explicit
about scope and lifetime.

### Copying When Not Necessary
`list(existing_list)` creates a shallow copy. If you just need to read, pass the
original. Use `copy.deepcopy` only when mutation isolation is actually required.

## Profiling Tools (for runtime analysis)

These tools complement static analysis:

- `tracemalloc` — built-in, traces memory allocations by source line
- `memory_profiler` — line-by-line memory usage decorator
- `objgraph` — visualize object reference graphs
- `pympler` — detailed object size tracking
- `guppy3` / `heapy` — heap analysis

## Framework-Specific Tips

### Django
- Use `.iterator()` on large QuerySets to avoid caching all rows.
- Use `.values_list(flat=True)` when you only need specific fields.
- Be careful with `prefetch_related` on large relation sets.

### Flask / FastAPI
- Avoid storing request-scoped data in module-level containers.
- Use streaming responses for large payloads.
- Clean up background task results to avoid accumulation.
