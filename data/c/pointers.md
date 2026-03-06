# Pointer Traps

- Dereferencing NULL — crash (usually), UB technically
- Pointer arithmetic past array bounds — UB even without dereference
- `int *p = arr; p[10]` when arr has 5 elements — silent corruption
- Comparing pointers from different arrays — UB, result meaningless
- `void*` arithmetic — not allowed in standard C (GCC extension)
- Casting `int*` to `char*` okay, reverse may violate alignment
- Function pointers with wrong signature — UB when called
- Returning `&local_var` — dangling pointer
