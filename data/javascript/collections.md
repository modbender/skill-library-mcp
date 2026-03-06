# Collection Traps

- `sort()` muta el original — y sin comparador es lexicográfico: [10, 2, 1]
- `reverse()` muta — usar `toReversed()` (ES2023) para copia
- `splice()` muta Y devuelve removidos — confusión de return
- `find()` devuelve undefined — igual que elemento undefined en array
- `indexOf()` con NaN devuelve -1 — NaN !== NaN, usar `includes()`
- `filter(Boolean)` remueve falsy — incluyendo 0 y "" que querías
- `[...array]` es shallow — objetos anidados comparten referencia
- `structuredClone()` deep pero no clona funciones, DOM nodes
- JSON parse/stringify pierde undefined, functions, Dates
- `for...in` incluye heredados — usar `Object.keys()` o `for...of`
- `delete obj.prop` es lento — asignar undefined si no importa
- `obj[key]` con key object — se convierte a "[object Object]"
- Set de objetos compara por referencia — {a:1} !== {a:1}
