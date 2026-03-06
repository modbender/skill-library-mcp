# Good First Issues — Pre-written

Copy these into GitHub Issues after creating the repo.

---

## Issue 1: Add multilingual complaint pattern keywords

**Labels:** `good first issue`, `enhancement`, `documentation`

### Context

`config.yaml` includes a `complaint_patterns` list — keywords that indicate the user is frustrated with repeated AI behavior. Currently the list is optimized for Korean (`"또?"`, `"다시"`, `"기억"`) with some English (`"still not"`, `"again"`).

Many OpenClaw users run in other languages. Adding more language support makes the skill work better out of the box for a wider audience.

### What needs to be done

Add complaint pattern keywords for at least **two additional languages** (e.g., Japanese, German, French, Spanish, Chinese) to `config.yaml` under `analysis.complaint_patterns`.

Guidelines:
- Phrases meaning "again", "you already said that", "I told you", "don't repeat", "remember"
- Keep them short — they're matched via `grep` in session logs
- Add a comment above each language group

Example format:
```yaml
complaint_patterns:
  # Korean
  - "또?"
  - "기억"
  # English
  - "again"
  - "still not"
  # Japanese (NEW)
  - "また"
  - "もう"
  # German (NEW)
  - "schon wieder"
  - "nochmal"
```

### Acceptance criteria

- [ ] At least 5 keywords per new language added
- [ ] Comments mark each language group
- [ ] `shellcheck` still passes (it's a YAML file — no shell impact)
- [ ] Add a note to `docs/` about language support

### Hints

- File to edit: `config.yaml`, under `analysis.complaint_patterns`
- Native speakers preferred — machine-translated phrases tend to be unnatural
- If you're unsure about a phrase, add it with a `# uncertain` comment

---

## Issue 2: Add `--dry-run` flag to generate-proposal.sh

**Labels:** `good first issue`, `enhancement`

### Context

`generate-proposal.sh` creates a proposal and optionally sends it to Discord. During development and testing, you want to see the proposal output without actually posting to Discord.

Currently there's no way to do this without editing the script or removing your Discord token.

### What needs to be done

Add a `--dry-run` flag (or `DRY_RUN=true` env var) to `scripts/generate-proposal.sh` that:

1. Runs all analysis and proposal generation normally
2. Prints the proposal to stdout instead of sending to Discord
3. Skips the Discord message send
4. Exits with code 0

Example usage:
```bash
DRY_RUN=true bash scripts/generate-proposal.sh
# or
bash scripts/generate-proposal.sh --dry-run
```

### Acceptance criteria

- [ ] `DRY_RUN=true bash scripts/generate-proposal.sh` prints proposal to stdout
- [ ] No Discord message sent in dry-run mode
- [ ] A log line confirms dry-run mode: `[DRY RUN] Proposal ready — skipping Discord delivery`
- [ ] `shellcheck` passes: `shellcheck scripts/generate-proposal.sh`
- [ ] `SKILL.md` or `README.md` mentions the dry-run option

### Hints

- Look for the Discord send logic in `scripts/generate-proposal.sh`
- Pattern for env var check: `if [[ "${DRY_RUN:-false}" == "true" ]]; then`
- Also check `scripts/analyze-behavior.sh` — it may have a similar pattern to follow

---

## Issue 3: Write a test fixture + smoke test script

**Labels:** `good first issue`, `testing`

### Context

There's currently no automated test suite. The CI only runs `shellcheck` and validates frontmatter. This means bugs in analysis logic aren't caught until someone actually runs the skill.

The smallest useful addition: a **smoke test** that runs `analyze-behavior.sh` against a fake session log fixture and verifies the output JSON structure.

### What needs to be done

1. Create `tests/fixtures/sample-sessions.json` — a minimal fake OpenClaw session log with:
   - 3-5 sessions
   - Some messages containing complaint keywords (`"또?"`, `"again"`)
   - Some tool calls (exec, message)
   - One session with repeated errors

2. Create `tests/smoke-test.sh` — a script that:
   - Points `analyze-behavior.sh` at the fixture (via env var override)
   - Runs the analysis
   - Checks the output JSON has expected keys: `sessions_analyzed`, `complaint_count`, `proposals`
   - Exits 0 on success, 1 on failure

3. Add the smoke test to `.github/workflows/ci.yml`:
```yaml
- name: Run smoke test
  run: bash tests/smoke-test.sh
```

### Acceptance criteria

- [ ] `bash tests/smoke-test.sh` exits 0 with fixture data
- [ ] CI runs smoke test on every PR
- [ ] `shellcheck tests/smoke-test.sh` passes
- [ ] Fixture is clearly fake (no real session data)
- [ ] README mentions how to run tests locally

### Hints

- Look at how `analyze-behavior.sh` reads session files — you'll need to match that format
- The fixture can be minimal — 3 sessions with ~5 messages each is enough
- Check `docs/architecture.md` for the session log format
- Use `jq` to validate JSON output: `echo "$OUTPUT" | jq '.sessions_analyzed' > /dev/null`
