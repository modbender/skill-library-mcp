# Async Traps

- `new Promise(async (resolve) => {})` — async executor swallows errors
- `.then()` sin `.catch()` — unhandled rejection silenciosa
- `return promise` vs `return await promise` en try/catch — solo await catchea
- `await` fuera de async — syntax error (top-level await solo en modules)
- `await` en loop — secuencial, usar `Promise.all` para paralelo
- Olvidar `await` — variable es Promise, no valor
- `forEach(async () => {})` — NO espera, iteraciones corren paralelas
- `Promise.all` un reject — todo falla, usar `allSettled` para todos los resultados
- Múltiples awaits sin coordinar — order impredecible, race conditions
- Error en Promise dentro de setTimeout — unhandled, no está en chain
- Top-level await error en module — module no carga
