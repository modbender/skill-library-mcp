# STL Traps

- Iterator invalidation — `vector` realloc invalidates ALL iterators
- `erase` in loop — returns next iterator, use `it = v.erase(it)`
- `map[]` creates entry — use `find()` or `contains()` to check existence
- `string::c_str()` — pointer invalid after string modified
- `vector<bool>` — not real bools, proxy objects, weird behavior
- `reserve` vs `resize` — `reserve` doesn't change size, `resize` does
- `emplace` vs `push` — `emplace` constructs in place, avoids copy
- Range `erase` — `v.erase(remove(...), v.end())` for remove-erase idiom
