# Metaprogramming Traps

- `define_method` — captures closure, be careful with loop variables
- `eval` string — security risk, avoid with user input
- `class_eval` vs `instance_eval` — class_eval defines instance methods, instance_eval defines singleton
- `const_get` with user input — can access any constant, security risk
- `method(:name)` — raises NameError if method doesn't exist
- `send` bypasses visibility — can call private methods
- `public_send` — respects visibility, safer
- `extend` adds to singleton class — affects only that instance
- `included` callback — fires when module included, not when methods called
