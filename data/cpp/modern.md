# Modern C++ Traps

- Move leaves valid state — but unspecified, don't use after move
- `auto` deduces value — `auto x = ref` copies, use `auto&` for reference
- Initializer list — `{}` prefers initializer_list ctor over others
- Lambda capture — `[=]` copies, `[&]` refs, `[this]` captures this
- `std::move` doesn't move — just casts to rvalue, move ctor does work
- Forwarding reference — `T&&` with deduction is universal, not rvalue
- `constexpr` if — evaluated at compile time, enables template branches
- Structured bindings — `auto [a, b] = pair;` copies unless `auto& [a,b]`
