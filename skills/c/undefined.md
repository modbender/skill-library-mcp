# Undefined Behavior Traps

- Modifying string literal — `char *s = "x"; s[0] = 'y';`
- Accessing uninitialized variable — any value, optimizer assumes never happens
- Signed overflow — `INT_MAX + 1` is UB, not wrap
- NULL dereference — UB, optimizer may remove null checks
- Missing return in non-void function — UB if caller uses value
- Shift by negative or >= width — `1 << 32` on 32-bit int is UB
- Modifying same object twice between sequence points — `i = i++`
- Type punning through pointer cast — use union or memcpy
- Strict aliasing violation — `*(int*)&float_var` is UB
- Infinite loop without side effects — may be optimized away
