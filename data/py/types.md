# Type Traps

- Mutable default args — `def f(x=[])` shares list across calls, use `None`
- `is` vs `==` — `is` checks identity, `==` checks value; `a is b` fails for equal objects
- Integer caching — `256 is 256` is True, `257 is 257` may be False
- Float comparison — `0.1 + 0.2 != 0.3`, use `math.isclose()`
- `None` check — use `is None`, not `== None`
- Type hints don't enforce — `def f(x: int)` accepts strings at runtime
- `bool` subclass of `int` — `True + True == 2`, `False == 0`
