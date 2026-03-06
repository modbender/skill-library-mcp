# Troubleshooting Fabric API requests

This is a quick playbook for debugging the most common failures when using the Fabric HTTP API via this skill.

## Always keep error bodies visible

When debugging schema validation (400s), the response body is usually the fastest way to fix the payload.

- If you use the Node/Python helpers shipped with this skill:
  - They print `HTTP <code> <reason>` to stderr on errors **and still print the response body**, then exit non‑zero.
  - Node: `node {baseDir}/scripts/fabric.mjs ...`
  - Python: `python3 {baseDir}/scripts/fabric.py ...`

- If you use raw `curl`, prefer:
  - `--fail-with-body` (shows 4xx/5xx bodies; newer curl)
  - `-sS` (silent, but still prints errors)

## 400 Bad Request

Almost always schema validation.

Checklist:

- Are you using the correct endpoint?
  - Create “note” → `POST /v2/notepads` (not `/v2/notes`)
- Did you include all required fields?
  - Notepad create: `parentId` and (`text` or `ydoc`)
  - Bookmark create: `url` and `parentId`
  - Folder create: `parentId` (and `name` if you want one)
- Is `parentId` valid?
  - UUID or `@alias::inbox` / `@alias::bin` for create endpoints
- Are `tags` shaped correctly?
  - `tags: [{"name":"x"},{"id":"<uuid>"}]`

### Common tag mistakes

- `tags: ["a","b"]` → invalid (strings)
- `tags: [["a"],["b"]]` → invalid (nested arrays)
- `tags: [{ "name": ["a"] }]` → invalid (name must be string)

## 401 Unauthorized / 403 Forbidden

- 401 usually means the API key is missing/invalid.
- 403 usually means:
  - the key lacks access to the resource (workspace permissions), or
  - your plan/subscription hit a limit.

Action:

- Stop and surface the `detail` / error message to the user.
- Do **not** brute-force retries.

## 404 Not Found

Most commonly:

- Wrong path (`/v2/notes` vs `/v2/notepads`)
- Wrong `resourceId`
- Wrong `parentId` (UUID doesn’t exist / you don’t have access)
- Trying to use an alias where only UUID is accepted (e.g. `POST /v2/resources/filter`)

## 429 Too Many Requests

Treat as rate limiting.

Recommended behaviour:

- Back off with jitter (sleep a bit, try again).
- Retry **reads** safely.
- Avoid automatic retries on creates unless you’ve built idempotency/dedupe checks (otherwise you can create duplicates).

## 5xx Server errors

Likely transient:

- Retry with exponential backoff.
- If repeatable, capture the full response body and report.

## Debugging “parentId alias” issues

If `@alias::inbox` works for creates but you need the actual UUID (e.g. to list children):

1) `GET /v2/resource-roots`
2) Find the SYSTEM inbox root
3) Use its `folder.id` as the UUID for `POST /v2/resources/filter`

## Capture a minimal repro payload

When you hit validation errors:

1) Remove optional fields until it works (start with just required fields)
2) Add fields back one by one:
   - first `name`
   - then `tags`
   - then `comment`

This makes it obvious which field is breaking schema validation.
