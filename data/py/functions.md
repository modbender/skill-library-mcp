# Function Traps

- Mutable default arg — evaluated ONCE at definition, shared across calls
- `*args` after keyword-only — `def f(*, name)` forces keyword
- Late binding closures — `lambda: i` captures variable, not value
- `return` in finally — overrides return/exception from try block
- Generator exhausted — can only iterate once, `list(gen)` to reuse
- `yield` makes function generator — returns iterator, not value
- `@decorator` without parens — `@deco` vs `@deco()` are different
- `global` vs `nonlocal` — `global` for module, `nonlocal` for enclosing
