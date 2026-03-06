# Generic Traps

- `useState<User>()` infiere `User | undefined` — manejar undefined inicial
- `Array.filter(x => x.active)` no narrowea — necesita type guard: `.filter((x): x is Active => x.active)`
- `Promise.all([a(), b()])` infiere tupla solo con `as const`
- `<T = any>` escapa el `any` al resto del código
- `<T extends object>` permite arrays — usar `Record<string, unknown>` para objetos
- `<T extends string>` con literal infiere `string`, no el literal
- `keyof T` en función genérica es `string | number | symbol`
- Arrays covariantes — `Dog[]` assignable a `Animal[]` pero push de Cat rompe runtime
- Function params contravariantes — `(Animal) => void` NO assignable a `(Dog) => void`
- `{ [K in keyof T]: X }` pierde modificadores — usar `-?` o `-readonly`
- `Partial<T>` y `Required<T>` son shallow — no afectan nested
