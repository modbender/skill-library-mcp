# Class Traps

- Class attribute shared — `class A: items = []` shared by all instances
- `__init__` returns None — can't `return value`, use `__new__` for singletons
- Mutable class default — same as function default trap, use `None` + init
- `super()` in multiple inheritance — follows MRO, not just parent
- `__slots__` breaks `__dict__` — can't add arbitrary attributes
- `@property` setter needs getter — define getter first with `@property`
- `__eq__` without `__hash__` — makes class unhashable, can't use in sets
- Private `__name` mangling — `_ClassName__name`, not truly private
