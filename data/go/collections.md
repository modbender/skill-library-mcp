# Slice, Map, String Traps

- `b := a[1:3]` shares backing array — no copy
- Append may or may not reallocate — never assume capacity
- Large slice keeps entire backing array alive — copy if extracting small piece
- `append([]int{}, a...)` es copy — `copy()` necesita pre-allocation
- Nil slice vs empty slice — `var s []int` ≠ `s := []int{}`
- Slice to function shares memory — mutations visible to caller
- `clear(s)` zeros but keeps length — use `s = s[:0]` to empty
- Nil map read returns zero — write panics
- Map iteration order random — don't rely on it
- Maps not concurrent-safe — use `sync.Map` or mutex
- `&m[key]` doesn't compile — can't address map element
- Delete during iteration safe — add may skip or revisit
- `len(s)` is bytes — use `utf8.RuneCountInString` for chars
- `s[i]` is byte not rune — `for _, r := range s` for runes
- String concat in loop O(n²) — use `strings.Builder`
- `string(65)` is "A" — use `strconv.Itoa` for decimal
