# Array Traps

- `array_merge()` reindexes — use `+` operator to preserve numeric keys
- Unset doesn't reindex — `unset($arr[1])` leaves gap, `array_values()` to fix
- `foreach` by reference — `foreach($arr as &$v)` keeps ref after loop, unset it
- `$arr[] = x` vs `$arr[0] = x` — first appends, second replaces
- `array_filter()` no callback — removes falsy INCLUDING `"0"` and `0`
- `array_map` null callback — zips arrays together, not what you expect
- `array_keys()` strict — pass third param `true` for strict comparison
- Negative index doesn't wrap — `$arr[-1]` is literal key `-1`, not last element
