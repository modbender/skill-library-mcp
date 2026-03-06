# Memory Management Traps

- `malloc(0)` may return NULL or valid pointer — implementation-defined, always check
- `realloc(ptr, 0)` may free and return NULL — don't assign directly to ptr (leak on failure)
- `free()` on stack memory — crash or corruption
- Forgetting to free in all exit paths — use goto cleanup pattern or wrapper
- `calloc` zeros memory, `malloc` doesn't — uninitialized reads are UB
- Double free — undefined behavior, often exploitable security bug
- Use after free — dangling pointer access, UB
- Memory leak in loop — allocate before loop or free inside
- `sizeof(*ptr)` vs `sizeof(type)` — prefer former, survives type changes
