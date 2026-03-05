# Collection Traps

- Modify list while iterating — skips elements, iterate over copy `list(x)`
- Dict keys mutated — if key object changes hash, dict lookup fails silently
- `dict.get()` returns None — can't distinguish missing key from None value
- List slice creates copy — `a[:]` is new list, but shallow (nested objects shared)
- `in` on list is O(n) — use `set` for membership testing
- Empty list/dict is falsy — `if not my_list:` catches empty AND None
- `+=` on tuple fails — tuples immutable, but `a = a + (x,)` works
- `list * n` shares refs — `[[]] * 3` creates 3 refs to SAME inner list
