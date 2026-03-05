# Object Traps

- String mutation — `str.upcase!` modifies in place, `upcase` returns new
- Default argument evaluated once — `def foo(arr=[])` shares array across calls
- `dup` vs `clone` — `clone` copies frozen state and singleton methods, `dup` doesn't
- `freeze` is shallow — frozen array's elements can still be modified
- Symbol memory — symbols never garbage collected (before 2.2), avoid dynamic symbols
- `nil.to_s` returns "" — silent conversion can hide bugs
- Integer division — `5/2` is 2, use `5.0/2` or `5.fdiv(2)` for float
- Range exclude end — `(1...5)` excludes 5, `(1..5)` includes 5
