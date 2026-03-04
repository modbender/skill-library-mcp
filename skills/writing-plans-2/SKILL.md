---
name: writing-plans
description: Break design into 2-5 minute tasks with verification steps.
---

# Writing Plans Skill

## When to Use

After design approval (brainstorming complete).

## Task Structure

Each task must have:
1. **Goal** (1 sentence)
2. **Files** (exact paths)
3. **Implementation** (code snippet or pseudo-code)
4. **Verification** (command to run + expected output)
5. **Estimated Time** (2-5 min ideal)

## Plan Template

```markdown
# Implementation Plan: [Feature Name]

## Tasks

### Task 1: [Goal]
**Files:** `src/file.js`
**Implementation:**
```javascript
// Add function here
function cacheFetch(key) {
  // ...
}
```
**Verification:**
```bash
npm test -- cache.test.js
# Expected: 1 passing
```
**Estimated Time:** 3 min

### Task 2: [Goal]
[... repeat]
```

Save to: `docs/plans/YYYY-MM-DD-feature-name.md`

## Quality Checklist

Before finalizing plan:
- [ ] Every task has exact file paths
- [ ] Every task has verification command
- [ ] No task >5 min (if yes, split)
- [ ] Tasks are ordered (dependencies first)
- [ ] Plan is reviewable (concrete, not vague)

## Anti-Patterns

❌ Vague tasks ("Improve caching")
❌ No verification steps
❌ Tasks without file paths
❌ Monster tasks (>10 min)

## Example

Bad Task:
```
Task 1: Add caching
- Implement cache layer
```

Good Task:
```
Task 1: Add in-memory cache for API responses
**Files:** `src/cache.js` (new), `src/api.js` (modify)
**Implementation:**
```javascript
// cache.js
const cache = new Map();
export function get(key) { return cache.get(key); }
export function set(key, val, ttl) { 
  cache.set(key, val);
  setTimeout(() => cache.delete(key), ttl);
}

// api.js (modify fetchUser)
const cached = cache.get(`user:${id}`);
if (cached) return cached;
// ... existing fetch logic
cache.set(`user:${id}`, result, 60000);
```
**Verification:**
```bash
node -e "const c = require('./src/cache'); c.set('test', 42, 1000); console.log(c.get('test'));"
# Expected: 42
```
**Estimated Time:** 4 min
```
