# Spec Template

Use this template when generating `spec-phase-{n}.md` for each approved phase.

---

# Implementation Spec: {Project Name} - Phase {N}

**Contract**: ./contract.md
**PRD**: ./prd-phase-{N}.md *(omit if no PRDs were generated)*
**Estimated Effort**: {T-shirt size: S/M/L/XL}

## Technical Approach

{High-level description of the implementation strategy. 2-3 paragraphs covering:
- Overall architecture approach
- Key technical decisions and rationale
- Patterns or frameworks to use}

## File Changes

### New Files

| File Path               | Purpose                                    |
| ----------------------- | ------------------------------------------ |
| `{path/to/new/file.ts}` | {Brief description of what this file does} |

### Modified Files

| File Path                    | Changes                      |
| ---------------------------- | ---------------------------- |
| `{path/to/existing/file.ts}` | {What to add/change and why} |

## Implementation Details

### {Component/Feature 1}

**Pattern to follow**: `{path/to/similar/implementation.ts}` (if applicable)

**Overview**: {1-2 sentences describing this component}

```typescript
// Key interfaces or types
interface {InterfaceName} {
  {property}: {type};
}

// Key function signatures
function {functionName}({params}): {returnType} {
  // Implementation notes
}
```

**Key decisions**:
- {Decision 1 and rationale}
- {Decision 2 and rationale}

**Implementation steps**:
1. {Step 1}
2. {Step 2}
3. {Step 3}

### {Component/Feature 2}

{Same structure as above}

## Data Model

{If applicable - database schema changes, state shape, etc.}

### Schema Changes

```sql
-- New tables
CREATE TABLE {table_name} (
  id UUID PRIMARY KEY,
  {column} {type},
  created_at TIMESTAMP DEFAULT NOW()
);
```

### State Shape

```typescript
interface {StateName} {
  {property}: {type};
}
```

## API Design

{If applicable - new or modified endpoints}

### New Endpoints

| Method   | Path                  | Description    |
| -------- | --------------------- | -------------- |
| `POST`   | `/api/{resource}`     | {What it does} |
| `GET`    | `/api/{resource}/:id` | {What it does} |

### Request/Response Examples

```typescript
// POST /api/{resource}
// Request
{
  "{field}": "{value}"
}

// Response
{
  "id": "uuid",
  "{field}": "{value}"
}
```

## Testing Requirements

### Unit Tests

| Test File                | Coverage        |
| ------------------------ | --------------- |
| `{path/to/test.spec.ts}` | {What it tests} |

**Key test cases**:
- {Test case 1}
- {Test case 2}
- {Edge case 1}
- {Error case 1}

### Integration Tests

| Test File                       | Coverage        |
| ------------------------------- | --------------- |
| `{path/to/integration.spec.ts}` | {What it tests} |

## Error Handling

| Error Scenario | Handling Strategy                                           |
| -------------- | ----------------------------------------------------------- |
| {Scenario 1}   | {How to handle - e.g., "Return 400 with validation errors"} |
| {Scenario 2}   | {How to handle - e.g., "Retry 3x with exponential backoff"} |

## Validation Commands

```bash
# Type checking
{pnpm run typecheck | npm run typecheck | etc.}

# Linting
{pnpm run lint | npm run lint | etc.}

# Unit tests
{pnpm run test | npm run test | etc.}

# Build
{pnpm run build | npm run build | etc.}
```

## Open Items

{Any remaining questions or decisions to make during implementation. Remove if none.}

- [ ] {Open item 1}
- [ ] {Open item 2}

---

_This spec is ready for implementation. Follow the patterns and validate at each step._
