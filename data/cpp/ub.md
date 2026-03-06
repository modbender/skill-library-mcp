# Undefined Behavior Traps

- Signed overflow — `INT_MAX + 1` is UB, use unsigned or check
- Shift too far — `1 << 32` on 32-bit is UB
- Null dereference — UB, not just crash
- Uninitialized read — UB, variable has indeterminate value
- Out of bounds — array access beyond size is UB
- Strict aliasing — casting pointer types breaks optimizer assumptions
- Sequence points — `i++ + i++` is UB, order undefined
- ODR violation — same name, different definition across TUs
