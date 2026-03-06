# Property Wrappers Gotchas

- Wrapped value initialized before `self` available — can't access instance in property wrapper init
- `projectedValue` ($prefix) can be any type — read docs, it's not always a Binding
- `@propertyWrapper` needs `init(wrappedValue:)` — without it, can't use `= defaultValue` syntax
- Property wrappers break automatic Codable — add manual `CodingKeys` and `init(from:)`
- Structs with lazy property wrappers — copying struct recomputes lazy value

# Actors Advanced Traps

- `nonisolated` methods can't read actor-isolated stored properties — compiler error, use async method
- Actor reentrancy at every `await` — state may change between suspension points
- Protocol witnesses on global actors must be isolated — or explicitly `nonisolated`
- Distributed actors require all parameters/returns to be `Codable` and `Sendable`
- Actor-isolated closures can't escape to non-isolated contexts — use `@Sendable` and pass values

# Result Builders Traps

- `buildExpression` determines valid types — unclear errors if expression type not handled
- `buildOptional` required for bare `if` — without it, conditionals don't compile
- `buildEither(first:)` and `buildEither(second:)` required for `if-else`
- Complex type inference — builder methods order affects what compiles

# Macros (Swift 5.9+)

- Macro expansion errors point to usage site — actual bug is in macro definition
- Multiple attached macros can conflict — expansion order depends on declaration order
- Freestanding macros (`#macro`) produce expressions/declarations — attached (`@Macro`) modify declarations
- Macros operate on syntax only — can't inspect runtime values or types beyond what's written
