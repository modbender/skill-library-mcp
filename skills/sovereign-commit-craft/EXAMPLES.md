# Sovereign Commit Craft — Examples

Real-world examples demonstrating how to use this skill for commit messages, changelogs, and PR descriptions.

---

## Example 1: Write a Commit Message for a Diff

### User Prompt

> Write a commit message for this diff:

```diff
diff --git a/src/api/middleware/rateLimit.ts b/src/api/middleware/rateLimit.ts
new file mode 100644
index 0000000..a3b4c5d
--- /dev/null
+++ b/src/api/middleware/rateLimit.ts
@@ -0,0 +1,87 @@
+import { Request, Response, NextFunction } from 'express';
+import Redis from 'ioredis';
+
+interface RateLimitConfig {
+  windowMs: number;
+  maxRequests: number;
+  keyPrefix: string;
+}
+
+const DEFAULT_CONFIG: RateLimitConfig = {
+  windowMs: 60 * 1000,
+  maxRequests: 100,
+  keyPrefix: 'rl:',
+};
+
+export function createRateLimiter(
+  redis: Redis,
+  config: Partial<RateLimitConfig> = {}
+) {
+  const { windowMs, maxRequests, keyPrefix } = { ...DEFAULT_CONFIG, ...config };
+
+  return async (req: Request, res: Response, next: NextFunction) => {
+    const key = `${keyPrefix}${req.ip}`;
+    const current = await redis.incr(key);
+
+    if (current === 1) {
+      await redis.pexpire(key, windowMs);
+    }
+
+    res.setHeader('X-RateLimit-Limit', maxRequests);
+    res.setHeader('X-RateLimit-Remaining', Math.max(0, maxRequests - current));
+
+    if (current > maxRequests) {
+      const ttl = await redis.pttl(key);
+      res.setHeader('Retry-After', Math.ceil(ttl / 1000));
+      return res.status(429).json({
+        error: 'Too Many Requests',
+        retryAfter: Math.ceil(ttl / 1000),
+      });
+    }
+
+    next();
+  };
+}

diff --git a/src/api/routes/index.ts b/src/api/routes/index.ts
index 1234567..89abcde 100644
--- a/src/api/routes/index.ts
+++ b/src/api/routes/index.ts
@@ -1,10 +1,14 @@
 import { Router } from 'express';
+import Redis from 'ioredis';
+import { createRateLimiter } from '../middleware/rateLimit';
 import { userRoutes } from './users';
 import { productRoutes } from './products';
 import { orderRoutes } from './orders';

 const router = Router();
+const redis = new Redis(process.env.REDIS_URL);
+const rateLimiter = createRateLimiter(redis, { maxRequests: 100, windowMs: 60000 });

-router.use('/users', userRoutes);
-router.use('/products', productRoutes);
-router.use('/orders', orderRoutes);
+router.use('/users', rateLimiter, userRoutes);
+router.use('/products', rateLimiter, productRoutes);
+router.use('/orders', rateLimiter, orderRoutes);

diff --git a/src/api/middleware/rateLimit.test.ts b/src/api/middleware/rateLimit.test.ts
new file mode 100644
index 0000000..f1e2d3a
--- /dev/null
+++ b/src/api/middleware/rateLimit.test.ts
@@ -0,0 +1,54 @@
+import { createRateLimiter } from './rateLimit';
+import RedisMock from 'ioredis-mock';
+
+describe('createRateLimiter', () => {
+  let redis: RedisMock;
+  let limiter: ReturnType<typeof createRateLimiter>;
+
+  beforeEach(() => {
+    redis = new RedisMock();
+    limiter = createRateLimiter(redis, { maxRequests: 3, windowMs: 1000 });
+  });
+
+  it('allows requests under the limit', async () => {
+    const req = { ip: '127.0.0.1' } as any;
+    const res = { setHeader: jest.fn(), status: jest.fn().mockReturnThis(), json: jest.fn() } as any;
+    const next = jest.fn();
+
+    await limiter(req, res, next);
+    expect(next).toHaveBeenCalled();
+    expect(res.setHeader).toHaveBeenCalledWith('X-RateLimit-Remaining', 2);
+  });
+
+  it('blocks requests over the limit', async () => {
+    const req = { ip: '127.0.0.1' } as any;
+    const res = { setHeader: jest.fn(), status: jest.fn().mockReturnThis(), json: jest.fn() } as any;
+    const next = jest.fn();
+
+    // Exhaust the limit
+    await limiter(req, res, next);
+    await limiter(req, res, next);
+    await limiter(req, res, next);
+
+    // This should be blocked
+    next.mockClear();
+    await limiter(req, res, next);
+    expect(next).not.toHaveBeenCalled();
+    expect(res.status).toHaveBeenCalledWith(429);
+  });
+
+  it('sets correct rate limit headers', async () => {
+    const req = { ip: '192.168.1.1' } as any;
+    const res = { setHeader: jest.fn(), status: jest.fn().mockReturnThis(), json: jest.fn() } as any;
+    const next = jest.fn();
+
+    await limiter(req, res, next);
+    expect(res.setHeader).toHaveBeenCalledWith('X-RateLimit-Limit', 3);
+    expect(res.setHeader).toHaveBeenCalledWith('X-RateLimit-Remaining', 2);
+  });
+});
```

### Generated Commit Message

```
feat(api): add Redis-backed rate limiting to all API routes

The API had no protection against abuse or accidental traffic spikes.
A single client could overwhelm the server with unlimited requests,
degrading service for all users.

Add a configurable rate limiter using Redis sliding window counters.
Default: 100 requests per minute per IP. Returns standard rate limit
headers (X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After) so
clients can self-throttle.

Applied to /users, /products, and /orders routes.

Closes #301
```

### Reasoning

- **Type**: `feat` — this is new functionality (rate limiting did not exist before)
- **Scope**: `api` — the change lives entirely in the API layer
- **Subject**: describes the WHAT at a high level ("add Redis-backed rate limiting")
- **Body**: explains WHY (no abuse protection), WHAT the solution is (sliding window with Redis), and the defaults (100 req/min)
- **Tests included**: the test file was added in the same commit because the tests are for this specific feature. This is correct. Tests for the feature they test should be in the same commit.

---

## Example 2: Generate a Changelog from Commits

### User Prompt

> Generate a changelog for these commits since v1.5.0:

```
a1b2c3d feat(search): add autocomplete suggestions for product search
d4e5f6a fix(auth): prevent token refresh race condition on concurrent requests
b7c8d9e perf(db): add composite index on orders(user_id, created_at)
f0a1b2c feat(notifications): add in-app notification center with real-time updates
e3d4c5b fix(upload): handle UTF-8 filenames with special characters
a6b7c8d docs(api): document new search and notification endpoints
c9d0e1f build(deps): upgrade prisma from 5.8 to 5.10
d2e3f4a chore(lint): enable strict TypeScript checks
f5a6b7c feat(export): add CSV export for order history
b8c9d0e fix(ui): correct date picker timezone handling in Safari
a1b2c3d refactor(payments): extract payment processing into dedicated service
e4f5a6b test(search): add integration tests for autocomplete
c7d8e9f ci(deploy): add staging environment to deployment pipeline
d0e1f2a fix(auth): expire sessions after 30 days of inactivity
BREAKING: feat(api)!: change order list endpoint to return paginated responses
```

### Generated Changelog

```markdown
## [1.6.0] - 2026-02-23

### Added
- **Search autocomplete**: Product search now suggests results as you type,
  matching on product name, SKU, and category (#312)
- **Notification center**: In-app notifications with real-time updates. Get
  notified about order status changes, system announcements, and more (#325)
- **CSV export**: Export your complete order history as a CSV file from the
  Orders page (#341)

### Changed
- **BREAKING: Paginated order list**: The `GET /api/orders` endpoint now returns
  paginated responses with `{ data, pagination }` shape instead of a plain
  array. Default page size is 25. See [migration guide](docs/migration-1.6.md)
  for details (#350)
- Order queries are significantly faster thanks to new database indexes,
  especially for users with large order histories (#318)

### Fixed
- Token refresh no longer fails when multiple tabs send simultaneous
  requests — concurrent refresh attempts are now deduplicated (#315)
- File uploads with special characters in filenames (accents, CJK characters,
  emoji) now work correctly (#320)
- Date picker in Safari no longer shifts dates by one day due to timezone
  handling (#338)
- Sessions now properly expire after 30 days of inactivity, closing a
  security gap where old sessions persisted indefinitely (#345)

[1.6.0]: https://github.com/user/repo/compare/v1.5.0...v1.6.0
```

### Reasoning

- **Version**: 1.6.0 (MINOR bump) because there is a breaking change, but since it includes new features too and the breaking change uses `feat!`, a MINOR bump applies. *However*, the BREAKING CHANGE footer means this should actually be a **MAJOR** bump to 2.0.0. Let me correct:

**Corrected version: 2.0.0** because any BREAKING CHANGE triggers a MAJOR bump per semver.

- **Omitted from changelog**: `docs`, `build`, `chore`, `test`, `ci`, and `refactor` commits — these are internal and not user-facing
- **Included `perf`**: Listed under "Changed" because the performance improvement is noticeable to users
- **Breaking change**: Called out prominently with bold **BREAKING** prefix and migration guide link
- **Language**: Written for users ("Product search now suggests results") not developers ("Add Elasticsearch fuzzy query to /api/search")

---

## Example 3: Write a PR Description

### User Prompt

> Write a PR description for these changes. The branch is `feature/user-preferences` based off `main`. Here are the commits:

```
feat(settings): add user preference storage with JSON schema validation
feat(ui): add preferences panel to settings page
feat(api): add GET/PUT /api/users/:id/preferences endpoints
test(settings): add unit tests for preference validation
test(api): add integration tests for preferences endpoints
docs(api): document preferences API with request/response examples
fix(settings): handle missing preferences gracefully for new users
```

> The diff shows:
> - New `src/services/preferences.ts` service (120 lines)
> - New `src/api/routes/preferences.ts` route handler (85 lines)
> - New `src/ui/components/PreferencesPanel.tsx` React component (200 lines)
> - New `src/schemas/preferences.json` JSON schema (45 lines)
> - Modified `src/api/routes/index.ts` to mount preferences routes
> - Modified `src/ui/pages/Settings.tsx` to include PreferencesPanel
> - New test files (3 files, ~300 lines total)
> - Updated `docs/api.md` with new endpoints

### Generated PR Description

**PR Title**: `feat(settings): add user preferences with API and settings UI`

```markdown
## Summary

Add a complete user preferences system that lets users customize their
experience. Preferences are validated against a JSON schema, stored per-user,
and accessible via both the settings UI and REST API. New users get sensible
defaults without errors.

## Changes

- **Preferences service** (`src/services/preferences.ts`): Core logic for
  reading, writing, and validating user preferences against a JSON schema.
  Handles defaults for new users who have no saved preferences yet.
- **API endpoints** (`src/api/routes/preferences.ts`):
  - `GET /api/users/:id/preferences` — retrieve current preferences
  - `PUT /api/users/:id/preferences` — update preferences (validated)
- **Settings UI** (`src/ui/components/PreferencesPanel.tsx`): New panel on the
  Settings page with form controls for all preference options. Validates
  client-side before submission.
- **JSON schema** (`src/schemas/preferences.json`): Defines allowed preference
  keys, types, and constraints. Single source of truth for validation.
- **Route mounting**: Updated main router to mount `/preferences` routes.
- **Settings page**: Updated to include the new PreferencesPanel component.

## Type of Change

- [x] New feature (non-breaking change that adds functionality)

## Test Plan

- [x] Unit tests for preference validation (valid input, invalid input,
  missing fields, extra fields, type mismatches)
- [x] Unit tests for default preference generation for new users
- [x] Integration tests for GET endpoint (existing user, new user, invalid
  user ID)
- [x] Integration tests for PUT endpoint (valid update, schema violation,
  partial update, unauthorized access)
- [ ] Manual testing: create new account, verify defaults load, change each
  preference, refresh page, verify persistence
- [ ] Manual testing: verify preferences panel renders correctly on mobile

## Related Issues

Closes #278
Closes #291
Refs #250

## Checklist

- [x] Code follows project style guidelines
- [x] Self-review performed
- [x] Comments added for complex logic
- [x] Documentation updated (docs/api.md)
- [x] No new warnings introduced
- [x] Tests pass locally
```

### Reasoning

- **PR Title**: Uses `feat(settings)` as the primary type since the core feature is in the settings domain. Kept under 72 characters.
- **Summary**: Three sentences covering what (preferences system), how (JSON schema + API + UI), and an edge case handled (new users).
- **Changes**: Organized by component, includes file paths for new files, describes the responsibility of each piece.
- **Test Plan**: Specific test cases listed, not vague "tested the feature." Includes both automated and manual testing items, with the manual ones left unchecked since they need to be done during review.
- **Type of Change**: Single checkbox — this is purely a new feature with no breaking changes.
- **No Breaking Changes section**: Omitted entirely since there are none (the section says to omit it in that case).
- **No Screenshots section**: Omitted since the prompt didn't include any, but a reviewer might request them for the PreferencesPanel component.

---

## Example 4: Review and Improve Existing Commit Messages

### User Prompt

> Review these commit messages and suggest improvements:

```
1. fixed the login bug
2. Update deps
3. feat: Add new feature for searching products with autocomplete and fuzzy matching
4. refactor(auth): refactored the authentication module to use new patterns
5. Added tests
```

### Review Output

**Message 1**: `fixed the login bug`
- Missing type prefix
- Past tense instead of imperative mood
- Too vague — which login bug?
- **Improved**: `fix(auth): prevent crash on empty password submission`

**Message 2**: `Update deps`
- Missing type prefix
- Not imperative (should be lowercase after type)
- Too vague — which dependencies?
- **Improved**: `build(deps): upgrade express to 4.19 and prisma to 5.10`

**Message 3**: `feat: Add new feature for searching products with autocomplete and fuzzy matching`
- "Add new feature" is redundant — `feat` already signals a new feature
- Subject line is 73 characters (over the 72-char limit)
- "A" should be lowercase after the colon
- **Improved**: `feat(search): add autocomplete with fuzzy matching for products`

**Message 4**: `refactor(auth): refactored the authentication module to use new patterns`
- Past tense ("refactored") instead of imperative
- "to use new patterns" is vague — which patterns?
- **Improved**: `refactor(auth): extract token validation into dedicated middleware`

**Message 5**: `Added tests`
- Missing type prefix
- Past tense instead of imperative
- Too vague — tests for what?
- **Improved**: `test(auth): add unit tests for password reset flow`

---

## Example 5: Determine Version Bump from Commits

### User Prompt

> What should the next version be? Current version is 3.2.1. Here are the commits since that release:

```
fix(api): handle null response from external payment provider
fix(ui): correct currency formatting for Japanese Yen
perf(db): optimize user lookup query with covering index
docs(readme): update installation instructions for Node 20
```

### Analysis

```
Current version: 3.2.1

Commit analysis:
- fix(api): handle null response        -> PATCH
- fix(ui): correct currency formatting   -> PATCH
- perf(db): optimize user lookup query   -> PATCH
- docs(readme): update installation      -> No version impact

Highest impact: PATCH (no feat = no MINOR, no BREAKING = no MAJOR)

Next version: 3.2.2
```

**Reasoning**: All commits are bug fixes or performance improvements. No new features (`feat`) were added, so no MINOR bump. No breaking changes, so no MAJOR bump. The version should increment the PATCH number from 1 to 2.

---

## Example 6: Split a Large Commit

### User Prompt

> This commit message covers too many changes. Help me split it:

```
feat(dashboard): add analytics widget and fix sidebar and upgrade chart.js

Added the new analytics widget, fixed the sidebar overflow bug,
and upgraded chart.js to the latest version.
```

### Split Recommendation

This commit contains three unrelated changes. Split into:

**Commit 1** (dependency update first — it enables the feature):
```
build(deps): upgrade chart.js from 4.3 to 4.4

Needed for the new time-series chart type used in the analytics
widget. Also fixes a memory leak in the pie chart renderer.
```

**Commit 2** (bug fix — independent of the feature):
```
fix(dashboard): prevent sidebar overflow on screens under 768px

The sidebar navigation items wrapped incorrectly on narrow screens,
overlapping the main content area. Add overflow-y: auto and a
max-height constraint.

Closes #412
```

**Commit 3** (the actual feature):
```
feat(dashboard): add real-time analytics widget to overview page

Display active users, error rate, and deployment frequency in
auto-refreshing charts. Uses the new chart.js time-series type
for the activity timeline.

Closes #398
```

**Why this order?** The dependency upgrade is committed first because the feature depends on it. The bug fix is independent and could go before or after, but placing it between keeps the git log logical: prepare dependencies, fix existing issues, then add new functionality.
