# Modern JS Traps

- `obj?.method()` vs `obj.method?.()` — primero chequea obj, segundo method
- `a?.b.c` throws si a.b es null — solo cortocircuita cadena derecha
- `??=` solo asigna si null/undefined — no falsy
- No mezclar `??` con `&&`/`||` sin paréntesis — syntax error
- Destructuring default solo undefined, no null — `{a=1}={a:null}` → a es null
- Nested destructuring — `{a:{b}}={a:null}` throws
- `this` antes de `super()` — error en constructor
- Private `#field` accesibles con devtools — no realmente privados
- `class` no hoistea — reference error si usas antes de declarar
- Circular imports — pueden dar undefined, depende de orden
- `import *` objeto frozen — no puedes modificar exports
- `structuredClone()` no clona funciones — throws error
- Top-level await solo en modules — scripts normales syntax error
