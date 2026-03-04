# Ghost Catalog Category Codes

Quick reference for the 3-letter category codes used in `SOM-XXX-NNNN-vX.X.X` file IDs.

| Code | Category | Extensions / Patterns | Comment Style |
|------|----------|----------------------|---------------|
| `SCR` | Script | `.py`, `.sh`, `.ps1`, `.bat`, `.rb` | `#` |
| `DOC` | Document | `.md`, `.txt`, `.rst`, `.adoc` | `<!-- -->` for md, `#` for rst |
| `CFG` | Config | `.json`, `.yaml`, `.yml`, `.toml`, `.env`, `.ini`, `.config.js`, `.config.ts` | varies |
| `SCH` | Schema | `.prisma`, `.graphql`, `.sql`, `.xsd` | `--` for sql, `#` for prisma |
| `CMP` | Component | `.tsx`, `.jsx`, `.vue`, `.svelte` | `//` or `{/* */}` |
| `TST` | Test | `*.test.*`, `*.spec.*`, `*_test.*` | matches source lang |
| `DAT` | Data | `.csv`, `.json` (data), `.db`, `.sqlite` | N/A (skip binary) |
| `STY` | Style | `.css`, `.scss`, `.less`, `.sass` | `/* */` |
| `LIB` | Library | `.ts`, `.js` (lib/ modules) | `//` |
| `API` | API Route | `route.ts`, `route.js` in `app/api/` | `//` |
| `UTL` | Utility | Helper modules, shared utils | `//` |
| `HKS` | Hooks | React hooks (`use*.ts`), git hooks | `//` or `#` |
| `MDW` | Middleware | `middleware.ts`, `middleware.js` | `//` |
| `LAY` | Layout | `layout.tsx`, `layout.jsx` | `//` |
| `PAG` | Page | `page.tsx`, `page.jsx` | `//` |

## Determining Category

Priority rules (first match wins):

1. **Filename patterns**: `route.ts` -> `API`, `page.tsx` -> `PAG`, `layout.tsx` -> `LAY`, `middleware.ts` -> `MDW`
2. **Test patterns**: `*.test.*` or `*.spec.*` -> `TST`
3. **Hook patterns**: `use*.ts` in hooks/ -> `HKS`
4. **Directory context**: `lib/` -> `LIB`, `app/api/` -> `API`, `components/` -> `CMP`, `scripts/` -> `SCR`
5. **Extension fallback**: `.py` -> `SCR`, `.md` -> `DOC`, `.css` -> `STY`, etc.
