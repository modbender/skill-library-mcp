# String Traps

- Missing null terminator — `strlen`, `printf %s`, `strcpy` read until they find `\0`
- `strncpy(dst, src, n)` doesn't null-terminate if src >= n — add `dst[n-1] = '\0'`
- `gets()` — never use, removed in C11, no bounds checking
- `sprintf` — use `snprintf` to prevent buffer overflow
- `strtok` modifies the string — don't use on literals or shared strings
- String literals are read-only — `char *s = "hi"; s[0] = 'H';` is UB
- `strlen` is O(n) — cache result in loops
- `strcmp` returns <0, 0, >0 — not just -1, 0, 1
