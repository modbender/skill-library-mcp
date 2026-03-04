---
name: Ruby
slug: ruby
version: 1.0.1
description: Write reliable Ruby avoiding mutable string traps, block pitfalls, and metaprogramming bugs.
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["ruby"]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Mutable strings, object equality | `objects.md` |
| Proc vs lambda, return behavior | `blocks.md` |
| Visibility, method_missing | `methods.md` |
| Array/hash mutation traps | `collections.md` |
| define_method, eval traps | `metaprogramming.md` |
| ActiveRecord, N+1, callbacks | `rails.md` |

## Critical Rules

- Strings are mutable — `s = "hi"; s << "!"; t = s` means t also has "!"
- `==` vs `equal?` vs `eql?` — `==` value, `equal?` identity, `eql?` hash equality
- Default hash value is shared — `Hash.new([])` shares same array, use block form
- `return` in proc returns from enclosing method — use lambda for local return
- Block variable shadows outer scope — `x = 1; [2].each { |x| }; x` is still 1 (3.0+)
- `method_missing` without `respond_to_missing?` — breaks `respond_to?` checks
- `private` in Ruby is per-object — `self.private_method` fails, implicit receiver works
- `||=` doesn't work for false/nil distinction — `false ||= true` replaces false
- Frozen string literals — `# frozen_string_literal: true` makes strings immutable
- `Symbol#to_proc` — `&:method_name` only works with no-argument methods
- `rescue => e` without type — catches StandardError, not Exception
- `ensure` always runs — even after return, use for cleanup
