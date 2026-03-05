# Coercion Traps

- `[] == false` es true — array → "" → 0
- `null == undefined` es true — pero `null === undefined` false
- `NaN !== NaN` — usar `Number.isNaN(x)` para detectar
- `{} == {}` es false — objetos comparan por referencia
- `0` y `""` son falsy — `if (count)` falla cuando count es 0
- `"0"` es truthy pero `"0" == false` — ambos true
- `??` solo null/undefined — `0 ?? default` devuelve 0
- `||` cualquier falsy — `0 || default` devuelve default
- `?.` devuelve undefined, no null — APIs que esperan null fallan
- `"" + {}` vs `{} + ""` — segundo es 0, parsed como bloque vacío
- `String(Symbol())` ok — pero `"" + Symbol()` throws
- `Number("")` es 0 — probablemente no lo que querías
- `1 + "2"` es "12" pero `1 - "2"` es -1 — + concatena, - coerce
- `[1,2] + [3,4]` es "1,23,4" — arrays a strings
