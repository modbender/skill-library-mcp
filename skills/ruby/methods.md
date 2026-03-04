# Method Traps

- `private` — no explicit receiver, `self.private_method` fails
- `protected` — can call on other instances of same class
- `method_missing` — must also define `respond_to_missing?`
- Method visibility is runtime — can be changed after definition
- `alias` vs `alias_method` — `alias` is keyword (no comma), `alias_method` is method
- `super` without parens — passes all original arguments
- `super()` with parens — passes no arguments
- `prepend` vs `include` — prepend inserts before class in ancestor chain
