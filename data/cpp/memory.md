# Memory Traps

- `new` without `delete` — leak, use smart pointers instead
- `delete` vs `delete[]` — wrong one is UB, `delete[]` for arrays
- Double delete — UB, set pointer to nullptr after delete
- Returning local address — `return &localVar` is dangling pointer
- `unique_ptr` in container — use `std::move()` to insert
- `shared_ptr` cycles — use `weak_ptr` to break circular references
- `make_shared` exception safety — single allocation, prefer over `new`
- Stack overflow — large arrays/recursion, use heap or increase stack
