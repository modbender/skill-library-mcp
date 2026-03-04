# Generics & Type Erasure

## Generics Traps
- Type erasure: generic type info gone at runtime — can't do `new T()` or `instanceof List<String>`
- Raw types bypass safety — `List list` allows any type, loses compile-time checks
- `List<Dog>` is not subtype of `List<Animal>` — use wildcards: `List<? extends Animal>`
- `<?>` is not same as `<Object>` — wildcard allows any type, Object only allows Object
- Generic arrays forbidden — `new T[10]` fails, use `ArrayList<T>` instead
