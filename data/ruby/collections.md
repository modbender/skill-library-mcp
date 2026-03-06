# Collection Traps

- `Hash.new(default)` — returns same object, mutations shared
- `Hash.new { |h,k| h[k] = [] }` — block form creates new object per key
- `array.map` returns new array — use `map!` for in-place
- `array.flatten` is recursive — use `flatten(1)` for one level
- `array.compact` removes nil — but not false, only nil
- Modify during iteration — may skip elements, iterate copy or use `delete_if`
- `Hash#each` order — guaranteed insertion order since Ruby 1.9
- `Set` requires `require 'set'` — not loaded by default
- `array - other` — uses `eql?` not `==`, subtraction by value
