# Migration Traps

- `noImplicitAny: false` esconde errores — código "compila" pero tipos wrong
- Callback params sin tipo son `any` silencioso — `arr.map(x => x.foo)` no falla
- `strictNullChecks: true` rompe mucho — localStorage.getItem devuelve `string | null`
- `strictPropertyInitialization` requiere init en constructor — o usar `!`
- `as Type` no valida nada — `"hello" as number` compila
- `as unknown as Type` escape total — evitar
- JSON.parse devuelve `any` — necesita assertion o validación
- `@types/x` puede estar desactualizado vs el paquete
- `skipLibCheck: true` esconde errores en tus .d.ts también
- `import x from "cjs"` vs `import * as x from "cjs"` — diferente comportamiento
- `// @ts-ignore` se propaga — usar `@ts-expect-error` que falla si no hay error
- `any` temporal se queda para siempre — mejor `unknown` desde el inicio
- `outDir` no limpia archivos viejos — .js huérfanos causan bugs
