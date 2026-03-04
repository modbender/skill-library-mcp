# Ghostclaw Reference — Stack Patterns

This document outlines architectural quality heuristics for different technology stacks.

## Node / React

### Vibe Health Indicators

**Good:**
- Small, focused components (<200 LOC)
- Clear separation: routes → controllers → services → repositories
- Thin controllers; business logic in services
- Dependency injection via constructor or context
- Consistent naming (camelCase functions, PascalCase classes)
- Minimal prop drilling (use context/state mgmt)

**Bad (Ghosts):**
- God components (UI + logic + data fetching)
- Services calling controllers (inverted flow)
- `any` overuse in TypeScript (type ghosts)
- Mixed concerns in single files (AuthGhost, DbGhost, ApiGhost)
- Circular dependencies between modules

### Refactor Templates

- **Extract Service**: Move business logic from route/controller to `services/`
- **Introduce Repository**: Abstract data access behind an interface
- **Split Component**: Break large component into smaller presentational ones

## Python (Django / FastAPI)

### Vibe Health Indicators

**Good:**
- Django apps have single responsibility (users, payments, etc.)
- Services layer separate from views/models
- Fat models only when truly domain-rich; otherwise service objects
- Dependency injection via function params or class init
- Clear async boundaries (async all the way down or not at all)

**Bad (Ghosts):**
- Views doing ORM queries and business logic (ViewGhost)
- Models with hundreds of lines (GodModel)
- Mixing async/sync without clear boundaries
- Utility functions scattered instead of in `utils/` modules

### Refactor Templates

- **Extract Service**: Create `services/` module for business logic
- **Split Model**: Break giant models into composition of smaller value objects
- **Async-ify**: Move blocking I/O to threadpool; ensure consistent async usage

## Go

### Vibe Health Indicators

**Good:**
- Packages are cohesive; small stdlib-style APIs
- Interfaces define behavior, not implementation
- Error handling explicit; no panic in library code
- Clear dependency direction (inner layers don't import outer)

**Bad (Ghosts):**
- Giant packages (50+ files, mixed concerns)
- Interface{} overuse (AnyGhost)
- Deeply nested package hierarchies
- Business logic in handlers (HandlerGhost)

### Refactor Templates

- **Extract Interface**: Define small interfaces close to consumer
- **Package Split**: Move unrelated code to separate packages
- **Handler Thinning**: Move logic to service layer; handlers just delegate

---

**Note**: Ghostclaw scores based on file size distribution, coupling metrics (coming), and naming coherence.
