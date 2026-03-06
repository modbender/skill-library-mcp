# Module templates for deep (greybox) modules

These templates are **examples**, not mandates. The key idea is always the same:

- A module has a **small public interface**
- Everything else is **internal**
- External code imports from the public interface only
- Tests lock behaviour at the boundary

## TypeScript / JavaScript

### Recommended structure (single repo)

```
src/
  auth/
    index.ts        # public exports
    types.ts        # public types
    internal/       # implementation (not imported from outside)
      token.ts
      password.ts
      db.ts
    __tests__/      # boundary/contract tests
      auth.contract.test.ts
```

### Public interface pattern

`src/auth/index.ts`:

```ts
export type { User, Session, AuthError } from "./types";
export { login, logout, requireAuth, getCurrentUser } from "./internal/public-api";
```

`src/auth/types.ts`:

```ts
export type User = { id: string; email: string };
export type Session = { userId: string; token: string };

export type AuthError =
  | { type: "invalid-credentials" }
  | { type: "locked" }
  | { type: "unknown"; message: string };
```

Key rules:
- `index.ts` should be short and obvious.
- Prefer exporting **functions** over exporting internal classes.
- Keep error semantics explicit (union types / result objects).

### Result object pattern (optional)

For fragile boundaries, avoid throwing across module boundaries:

```ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```

## Python

### Recommended structure

```
src/
  billing/
    __init__.py     # public exports
    types.py        # public types (dataclasses / TypedDict)
    internal/
      invoices.py
      stripe_adapter.py
      db.py
    tests/
      test_billing_contract.py
```

`src/billing/__init__.py` should expose the stable API:

```py
from .types import Invoice, BillingError
from .internal.public_api import create_invoice, get_invoice

__all__ = ["Invoice", "BillingError", "create_invoice", "get_invoice"]
```

Enforcement options:
- Keep `internal/` as a convention, and enforce with import-linter.
- In larger systems, package each module as its own distribution with explicit exports.

## Go

Go gives you a built-in boundary mechanism:

```
billing/
  billing.go         # public package API
  types.go
  internal/
    db/
    stripe/
  billing_test.go    # contract tests at package level
```

Anything under `internal/` cannot be imported by other packages outside the parent tree.

## Java / Kotlin

Use packages + visibility:

```
src/main/java/com/acme/auth/
  AuthService.java        // public API
  AuthTypes.java
  internal/
    JwtTokens.java
    PasswordHasher.java
src/test/java/com/acme/auth/
  AuthContractTest.java
```

Prefer:
- `public` for interface surface
- package-private for internals (no modifier)
- enforcement via build tooling / architecture tests (ArchUnit)

## “Deep module” smell checks

A module is *too shallow* when:
- it is mostly re-exports of other modules
- it has many “helper” files but no cohesive interface
- consumers import lots of internals to “get work done”

A module is *deep enough* when:
- consumers can do their work via 3–12 exported functions/types
- most code lives behind the interface
- tests at the boundary make internal changes safe
