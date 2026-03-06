# Declaration File Traps

- `declare module "x"` requiere path EXACTO — `"lodash"` ≠ `"lodash/index"`
- Augmentation sin imports se vuelve global — añadir `export {}` para forzar módulo
- `declare const` sin valor crea global — puede colisionar
- `declare function` en módulo no es global — necesita `declare global {}`
- Archivos .d.ts sin import/export son scripts globales — legacy confuso
- `interface` se puede merge desde otros archivos — `type` no
- `paths` en tsconfig solo compilación — bundler necesita config separada
- `baseUrl` requerido para `paths` — fácil de olvidar
- `export default` en .d.ts problemático — preferir named exports
- `declare module "*.svg"` afecta TODOS los .svg — no tipos específicos
