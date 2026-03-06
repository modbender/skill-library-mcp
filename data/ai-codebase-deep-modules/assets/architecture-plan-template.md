# AI‑Friendly Refactor Plan (Deep Modules)

## 1. Current state summary
- Repo type:
- Language/tooling:
- Current pain:

## 2. Fast feedback loop
- Local:
  - `...`
- CI:
  - `...`
- Notes on speed / reliability:

## 3. Module Map
| Module | Responsibilities | Entrypoints | Key types | Current coupling risks |
|---|---|---|---|---|
| auth | ... | ... | ... | ... |

## 4. Proposed deep modules
- `auth`: ...
- `billing`: ...
- `video-editor`: ...

## 5. Interface specs
### Module: `auth`
**Public API**
- `login(...) -> ...`
- `requireAuth(...) -> ...`

**Invariants**
- ...

**Examples**
- ...

## 6. Filesystem changes (move plan)
- Create:
- Move:
- Delete:
- Temporary shims:

## 7. Boundary enforcement
- Rule set:
- Tooling:
- Where configured:

## 8. Testing strategy
- Contract tests to add first:
- Integration tests to keep/trim:
- Missing coverage risks:

## 9. Incremental migration steps
1. ...
2. ...
3. ...

## 10. Rollback plan
- ...
