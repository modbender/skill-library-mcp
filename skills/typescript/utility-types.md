# Utility Type Traps

- `Partial<T>` es shallow — nested siguen required
- `Required<T>` no quita `undefined` del union — sigue teniendo undefined
- `Omit<T, K>` no verifica que K existe — `Omit<User, "typo">` compila
- `Pick` con key inexistente también compila — sin validación
- `Record<string, T>` implica TODA key existe — acceso a inexistente devuelve T, no T|undefined
- `Record<K, V>` con K union no garantiza todas las keys
- `Extract<T, U>` devuelve `never` si no match — silenciosamente vacío
- `ReturnType<typeof fn>` con overload toma solo última signature
- `Parameters` igual con overloads — inconsistente
- `NonNullable<T>` quita null Y undefined — a veces solo quieres uno
- `Awaited<T>` unwrapea recursivamente — sorpresa con Promise<Promise<T>>
