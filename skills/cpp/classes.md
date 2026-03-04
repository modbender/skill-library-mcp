# Class Traps

- Rule of 3/5/0 — if custom destructor, need copy/move ctor and assignment
- Slicing — passing derived as base value copies only base part
- Virtual destructor — missing in base = UB when deleting derived via base ptr
- Pure virtual in destructor — can still define it, called during destruction
- Initialization order — members init in declaration order, not initializer list
- Most vexing parse — `A a()` declares function, not object; use `A a{}` 
- `explicit` constructor — prevents `A a = 5` implicit conversion
- `override` keyword — catches typos in virtual function signatures
