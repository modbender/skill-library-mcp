# Inversion Protocol — Coding Scenarios

Real-world examples showing how the protocol catches bugs, prevents bad
architecture, and improves debugging speed.

---

## Scenario 1: The Silent Data Corruption

**Task**: User asks to add a caching layer to their API responses.

### Without Inversion Protocol

Agent adds an in-memory cache with a 5-minute TTL. Code works. Tests pass.
Ships to production. Three days later, users report seeing stale data that
doesn't match the database. The cache doesn't invalidate on writes.

### With Inversion Protocol

```
[INVERSION PROTOCOL — FULL]
Goal: Add caching layer to API responses

INVERT: How would I cause stale data on purpose?
1. Cache reads but never invalidate on writes
2. Set TTL so long that changes are invisible to users
3. Cache user-specific data with a shared key
Present? → #1 is exactly what I'm about to do. My plan has no
write-through or invalidation logic.

PREMORTEM: The cache shipped and caused a data incident. Why?
1. Cache served stale data after a database write (most likely)
2. Cache key collision between different users' data
3. Memory leak from unbounded cache growth
Verifiable? → Yes. I need to add invalidation on mutations.

VIA NEGATIVA: The ONE thing I must NOT do?
→ Cache without invalidation strategy.
Am I about to do it? → Yes.

DECISION: Adjust. Add write-through invalidation before implementing.
```

**Result**: Catches the #1 caching bug before a single line is written.

---

## Scenario 2: The Refactor That Breaks Production

**Task**: User asks to extract duplicated validation logic into a shared utility.

### Without Inversion Protocol

Agent identifies 4 places with similar validation, extracts to a shared
`validateInput()` function. Tests pass. But one of the 4 call sites had a
subtle difference — it accepted `null` as valid for optional fields. The shared
function rejects `null`. A downstream form breaks silently.

### With Inversion Protocol

```
[INVERSION — QUICK]
Inverse: I'd break this by assuming all 4 call sites have identical behavior
Premortem: The refactor broke because one call site had a special case
Razor: Do NOT assume identical behavior without reading every caller
→ Adjust: Diff all 4 implementations before extracting
```

Agent diffs all 4 sites, discovers the `null` handling difference, and
parameterizes the shared function with an `allowNull` option.

**Result**: 30-second check prevents a subtle production regression.

---

## Scenario 3: The Debugging Death Spiral

**Task**: User reports "the app crashes on login." Agent has been investigating
for 10 minutes, has tried 3 different theories, none panned out.

### Without Inversion Protocol

Agent continues forward-searching: reads more logs, adds more debug prints,
tries a fourth theory. Another 15 minutes pass. Turns out the issue was in the
environment config, not the code at all.

### With Inversion Protocol (Stuck Mode)

```
[INVERSION PROTOCOL — STUCK MODE]
I've been trying to: Find why the app crashes on login
My approaches so far:
- Checked auth middleware (clean)
- Checked database connection (working)
- Checked session handling (no errors)

FULL INVERSION: How would I guarantee login NEVER works?
1. Point the auth service to a wrong URL
2. Set an expired or invalid API key in env
3. Misconfigure CORS so the browser blocks the request

Am I accidentally doing any of these?
→ Haven't checked env config yet. Checking...
→ AUTH_SERVICE_URL is set to the staging endpoint, not production.

REFRAME: The problem isn't in the code logic
but actually in the environment configuration.
```

**Result**: Inversion surfaces the environment issue in seconds by asking "how
would I CAUSE a login failure?" instead of "where in the code is the bug?"

---

## Scenario 4: The Overengineered Solution

**Task**: User asks to add a "dark mode toggle" to their settings page.

### Without Inversion Protocol

Agent creates a ThemeProvider context, a useTheme hook, a theme configuration
object with 47 CSS variables, a theme persistence layer using localStorage with
migration support, and a ThemeToggle component with animation. 200+ lines of
code for a toggle.

### With Inversion Protocol

```
[INVERSION — QUICK]
Inverse: I'd overcomplicate this by building a full theming system
Premortem: User rejects it because it's too complex for their needs
Razor: Do NOT build infrastructure when they asked for a toggle
→ Adjust: CSS class toggle + localStorage. 15 lines.
```

**Result**: Delivers exactly what was asked, not an architecture astronaut's
dream.

---

## Scenario 5: The Security Hole

**Task**: User asks to build a file upload endpoint.

### With Inversion Protocol

```
[INVERSION PROTOCOL — FULL]
Goal: Build a file upload endpoint

INVERT: How would I make this maximally insecure?
1. Accept any file type including .exe, .sh, .php
2. Use the user-provided filename directly (path traversal)
3. Store uploads in a publicly accessible directory
4. No file size limit (denial of service)
Present? → My initial plan accepts all types and uses original filenames.

PREMORTEM: The upload endpoint was exploited. Why?
1. Attacker uploaded a web shell via unrestricted file type
2. Path traversal via crafted filename overwrote server files
3. Massive file upload exhausted disk space
Verifiable? → Yes. Add allowlist, sanitize filename, set size limit.

VIA NEGATIVA: The ONE thing I must NOT do?
→ Use user-supplied filename without sanitization.
Am I about to do it? → Yes, my plan uses `req.file.originalname`.

DECISION: Adjust. Sanitize filename, restrict types, add size limit.
```

**Result**: Catches 4 security vulnerabilities before the first line of code.

---

## Pattern: When to Use Which Mode

| Situation | Mode | Time |
|-----------|------|------|
| Writing a new function | Quick Check | 5 sec |
| Refactoring across files | Full Protocol | 30 sec |
| Stuck debugging > 5 min | Stuck Mode | 30 sec |
| Destructive command (rm, DROP, etc.) | Full Protocol | 30 sec |
| Answering a factual question | Quick Check | 5 sec |
| Architecture decision | Full Protocol | 30 sec |
| User has corrected you already | Full Protocol | 30 sec |
