# Block/Proc/Lambda Traps

- `return` in proc — returns from enclosing method, not just the proc
- `return` in lambda — returns from lambda only, like a method
- Arity checking — lambda enforces argument count, proc doesn't
- `Proc.new` without block — captures block passed to enclosing method
- `yield` vs `block.call` — yield is faster but can't check `block_given?` after store
- Block to proc — `&block` in parameter converts block to proc
- Proc to block — `&proc` in call converts proc back to block
- Closure captures binding — variables captured by reference, not value
