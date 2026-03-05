# Optional Traps

- Force unwrap `!` crashes on nil — use `guard let` or `if let` instead
- Implicitly unwrapped optionals `String!` still crash if nil — only use for IBOutlets
- Optional chaining returns optional — `user?.name?.count` is `Int?` not `Int`
- `??` default value evaluates eagerly — use `?? { expensive() }()` for lazy
- Comparing optionals: `nil < 1` is true — unexpected sort behavior
