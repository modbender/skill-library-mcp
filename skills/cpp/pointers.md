# Pointer Traps

- Null dereference — UB, check before access
- Dangling pointer — points to freed memory, UB on access
- Wild pointer — uninitialized, random memory location
- Array decay — `int arr[10]` becomes `int*` when passed, loses size
- `void*` arithmetic — can't do math on void*, cast first
- Reference to temp — `const int& r = getVal()` extends lifetime, non-const doesn't
- Pointer aliasing — optimizer assumes pointers don't overlap unless `restrict`
- `reinterpret_cast` — no conversion, just reinterprets bits, usually wrong
