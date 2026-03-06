# Type Traps

- `==` coerces types — `"0" == false` is true, always use `===`
- `"10" == "10.0"` — string comparison converts to numbers if both numeric
- `0 == "any"` before PHP 8 — legacy code still has this bug
- `in_array()` loose — pass `true` as third param for strict
- `switch` uses loose comparison — use `match` in PHP 8+ for strict
- `empty("0")` is true — "0" is falsy, use `=== ""` or `strlen()`
- Type declarations coerce — `int` param accepts "123", use `strict_types`
