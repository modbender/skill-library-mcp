# Type Traps

- Signed integer overflow — UB, compiler may remove "impossible" checks
- `unsigned - unsigned` when result negative — wraps to large positive
- `-1 > 1u` is true — signed converts to unsigned, -1 becomes UINT_MAX
- `char` signedness is implementation-defined — use `signed char` or `unsigned char`
- `int x = 1 << 31` — UB if int is 32-bit (shifts into sign bit)
- `sizeof` returns `size_t` (unsigned) — mixing with signed in comparison is dangerous
- Float-to-int truncates — `(int)3.9` is 3
- `INT_MIN / -1` — overflow, UB
