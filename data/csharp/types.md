# Type Traps

- Struct is value type — assignment copies, modifications don't affect original
- Boxing allocates — `object o = 5;` creates heap allocation
- `readonly` field can still have mutable reference type — contents can change
- `default(int)` is 0, `default(bool)` is false — not always obvious
- Struct in interface variable — boxed, modifications lost
- `Equals` on struct — default uses reflection (slow), override for performance
- `==` on struct — not defined by default, must implement
- Nullable value type boxing — `int? x = null; object o = x;` results in null object
- `decimal` vs `double` — decimal is exact but slower, use for financial
