# Boundary enforcement patterns

The goal is simple: **prevent cross-domain imports** that make the codebase hard to navigate and refactor.

Start light (conventions), then add tooling as soon as drift appears.

## Shared principles

1. **One public entrypoint per module**
   - TS/JS: `src/<module>/index.ts`
   - Python: `src/<module>/__init__.py`
2. **No external imports from internal folders**
   - `src/<module>/internal/**` is off-limits
3. **Explicit dependency direction**
   - Agree a small set of “platform/shared” modules
   - Domain modules may depend on platform/shared, not on each other (unless explicitly allowed)

## TypeScript / JavaScript

### Option A — ESLint `no-restricted-imports` (pragmatic default)

Example idea (adjust paths to your repo):

- Allow: `import { login } from "@/auth"`
- Disallow: `import { hash } from "@/auth/internal/password"`

Config sketch:

```js
// .eslintrc.js
module.exports = {
  rules: {
    "no-restricted-imports": [
      "error",
      {
        patterns: [
          // Block importing internals from anywhere
          "**/internal/*",
          "**/internal/**",

          // Optional: block cross-feature imports (example)
          // "@/auth/**" may only be imported via "@/auth"
        ],
      },
    ],
  },
};
```

Add a **path alias** so the “public entrypoint only” rule is ergonomic:

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

Then keep module entrypoints short and stable:
- `src/auth/index.ts`
- `src/billing/index.ts`

### Option B — Packages with explicit exports

If you already use workspaces (`packages/*`), make each module a package and expose only the public surface.

Example:

```
packages/auth/
  package.json  # "exports" points to dist/index.js
  src/index.ts  # public API
  src/internal/ # private implementation
```

Consumers import `@acme/auth` only.

### Option C — Architecture tests (when you need stronger guarantees)

Write a test that fails on forbidden imports (many libraries exist; also easy to script with `grep`/AST parsing).

Keep it simple:
- fail on `../auth/internal`
- fail on `src/auth/` imports that aren’t `src/auth/index`

## Python

### Convention + Import Linter

Use a tool like `import-linter` (or a simple AST check) to enforce rules:

- `billing` may import `platform` but not `auth.internal`
- only `billing/__init__.py` is imported from outside

If you don’t want extra tooling yet:
- keep `internal/` as a convention
- enforce via PR review and a lightweight CI grep check

## Go

Use `internal/` packages to make illegal imports impossible.

If you still have cross-domain coupling, it usually comes from:
- shared types in the wrong place
- shared DB access logic
- shared configuration

Fix by extracting a `platform` package or by inverting dependencies via interfaces.

## JVM (Java/Kotlin)

Two solid options:
- **ArchUnit** tests: assert package dependency rules
- **JPMS / Gradle conventions**: split domains into modules

Even without tooling:
- keep “public API” classes in the top package
- keep internal classes package-private and under `.internal`

## Dealing with necessary cross-domain calls

Sometimes modules must interact. Prefer one of these:

1. **Service interface inversion**
   - `billing` defines `UserLookup` interface
   - `auth` implements it
   - wire together in a composition root

2. **Events**
   - `auth` emits `UserLoggedIn`
   - `billing` subscribes
   - avoids direct imports

3. **Shared primitives module**
   - move only truly generic types/utilities into `platform/` (or `shared/`)
   - keep it small; avoid turning it into a junk drawer
