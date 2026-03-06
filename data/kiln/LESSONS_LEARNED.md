# Kiln — Lessons Learned

Hard-won technical patterns and bug fixes. Consulted when hitting unfamiliar issues. **Append new entries under the relevant section when you learn something new.**

---

## Printer Adapter Patterns
<!-- Patterns related to PrinterAdapter interface, state mapping, data normalization -->

### Temperature validation belongs in the base class
Don't rely on each adapter individually validating temperature bounds — they won't. Put a shared `_validate_temp()` in the abstract `PrinterAdapter` base class and call it from every concrete `set_tool_temp()`/`set_bed_temp()`. The MCP tool layer should ALSO validate, giving defense-in-depth. Same principle applies to any safety-critical operation: validate at every layer, not just one.

### Negative temperatures bypass `temp > limit` checks
The G-code validator originally only checked `temp > MAX_TEMP`. Negative temperatures (e.g., `M104 S-50`) passed right through. Always check `temp < 0` explicitly. This is the kind of bug that's invisible in happy-path testing but catastrophic in adversarial scenarios.

## OctoPrint API Quirks
<!-- Non-obvious behaviors of the OctoPrint REST API -->

## MCP Server Patterns
<!-- FastMCP tool registration, response formatting, error propagation -->

### Never pass `**body` from HTTP requests to tool functions
`func(**body)` lets callers inject arbitrary keyword arguments. Use `inspect.signature()` to filter to only valid parameters and reject unknowns with a 400. This prevents parameter pollution attacks where extra keys override internal defaults.

### Sanitize tool results before feeding to LLM agents
Tool results from MCP tools are untrusted data — printer names, filenames, and API error messages can all contain prompt injection payloads. Always sanitize before passing to the LLM. Add a system prompt warning about untrusted tool results.

### PrusaSlicer has no `--printer` CLI flag — use `--load` only
PrusaSlicer's CLI does NOT have a `--printer` flag. The code assumed it did (like some other tools) and passed `--printer "Original Prusa MINI & MINI+"`, which caused `kiln slice --printer-id X` to fail with "Unknown option --printer". The correct approach: generate a complete `.ini` profile file via `slicer_profiles.py` and pass it with `--load profile.ini`. PrusaSlicer applies all printer settings from the INI file. **Always verify that CLI flags you're generating actually exist in the target tool's documentation.** Mocked tests hide this class of bug entirely since the subprocess never runs.

## CLI / Output Formatting
<!-- Click CLI patterns, JSON output, exit codes, config management -->

### Every CLI command must support `--json` output
Human-readable output is the default, but agents and scripts depend on `--json`. When adding a new command, always include the `json_mode` flag and route through `format_response()` or the appropriate `format_*()` helper in `output.py`. Test both modes.

### Use the standard JSON envelope for all responses
All JSON output follows `{"status": "success|error", "data": {...}, "error": {...}}`. Never return bare data or ad-hoc structures. Agents parse the envelope to determine success/failure.

### Error messages must include what, why, and what-to-try
Bad: `"Error: connection refused"`. Good: `"Failed to connect to printer at http://octopi.local: connection refused. Check that OctoPrint is running and the host is correct."` Include the printer name/host when available.

## Python / Build System
<!-- pyproject.toml, setuptools, import resolution, packaging -->

### Always use `python3` and `pip3` on macOS
`python` may not exist or point to system Python 2. This causes silent import failures or wrong package installations. All scripts, commands, and documentation must use `python3`/`pip3`.

### ALWAYS run Ruff lint before pushing — CI will catch what you don't
CI runs `ruff check` on every push and fails on any violation. The local `py_compile` check only catches syntax errors, NOT lint issues like unused variables (F841) or function-call-in-defaults (B008). **After any Python edits, run `cd kiln && python3 -m ruff check src/kiln/` before committing.** Common gotchas: (1) `except Exception as exc:` where `exc` isn't used after sanitizing error messages — use `except Exception:` instead; (2) FastAPI `Depends()`/`File()` in function param defaults triggers B008 — hoist to module-level singletons like `_auth_dep = Depends(verify_auth)`. Never leave CI red. Fix immediately if it fails.

### `from __future__ import annotations` in every file
This enables PEP 604 union syntax (`X | None`) and forward references. Without it, type hints that reference later-defined classes fail at import time. Add it as the first import in every new file.

## Testing Patterns
<!-- pytest, mocking HTTP calls, mocking hardware, test isolation -->

### Counting CLI commands: walk the Click tree programmatically, count both packages
Never grep `@.*command()` or count function defs to get the CLI command count — these miss subcommands inside groups and overcount helpers. The correct method:
```python
python3 -c "
import click, sys
sys.path.insert(0, 'kiln/src')
from kiln.cli.main import cli
def count(group, prefix=''):
    cmds = []
    for name, cmd in group.commands.items():
        full = f'{prefix} {name}'.strip()
        cmds += count(cmd, full) if isinstance(cmd, click.Group) else [full]
    return cmds
print(len(count(cli)))
"
```
Also count `octoprint-cli` separately — kiln3d exposes **two CLI packages** (`kiln` + `octoprint-cli`). The total is their sum. As of v0.1.0: kiln=89, octoprint-cli=13, total=102.

### Use `responses` library for HTTP mocking, not `unittest.mock.patch` on requests
The `responses` library intercepts at the transport level, catching issues that `mock.patch` misses (like session reuse, header propagation, retry logic). Use `@responses.activate` decorator on each test method. Only use `unittest.mock.patch` for non-HTTP mocking (filesystem, time, env vars).

### Test all enum values — exhaustive coverage prevents state mapping bugs
When testing state mapping (e.g., OctoPrint flags → PrinterStatus), write a test for EVERY enum value. State mapping bugs (like `cancelling` → BUSY instead of CANCELLING) are caught by exhaustive tests, not by testing a few happy paths.

### Test class docstrings list coverage areas; method names are self-documenting
Class-level docstring explains what's being tested and what's covered. Individual test methods don't need docstrings — the name `test_empty_host_raises` is clear enough.

## Release & Publishing

### Version bump requires 3 files, not just pyproject.toml
When bumping the version for a release, update: (1) `kiln/pyproject.toml` → `version`, (2) `server.json` → top-level `version` AND `packages[0].version`, (3) `docs/site/src/layouts/BaseLayout.astro` → `softwareVersion` in the JSON-LD block. The CI workflow auto-syncs `server.json` from the git tag at publish time, but keep the repo in sync too so `main` always reflects the current version.

### PyPI + MCP Registry are both automated on GitHub Release
`publish.yml` triggers on `release: [published]`. It runs tests, validates the tag matches `pyproject.toml`, publishes to PyPI via trusted publishing (OIDC, no token), then publishes to the MCP Registry via `mcp-publisher` with GitHub OIDC. No manual publish commands needed — just `gh release create vX.Y.Z`.

### ClawHub skill must be republished on version bumps
ClawHub doesn't auto-detect updates from the repo. When shipping a new version (new tools, adapters, or SKILL.md changes), republish: `clawhub publish .dev --slug kiln --name "Kiln" --version X.Y.Z --tags "3d-printing,manufacturing,printer,mcp,octoprint,bambu,moonraker,klipper,prusa,ai-agent" --changelog "summary"`. This is part of the release checklist — don't skip it.

## Documentation & Content Updates
<!-- Rules for what to update, what to leave alone -->

### Never edit old blog posts to update counts or stats
Blog posts are dated content — they were accurate when published. When updating tool counts, CLI counts, test counts, etc. across the codebase, update README, docs, website components, and marketing pages — but **never** blog posts under `docs/site/src/pages/blog/`. Those are historical records. Only edit blog posts if explicitly told to.

## Project Structure & File Location
<!-- Where files live, directory conventions, common lookup mistakes -->

### Internal docs live in `.dev/`, not the repo root
All internal working documents (`TASKS.md`, `COMPLETED_TASKS.md`, `LESSONS_LEARNED.md`, `LONGTERM_VISION_TASKS.md`, `SWARM_GUIDE.md`, etc.) live in `.dev/`. When the user references a file by name (e.g., "longterm_vision_tasks.md"), check `.dev/` first — don't waste time globbing the entire repo. The Project Structure Quick Reference in `CLAUDE.md` documents this layout. **Read it before searching.**

## Configuration & Environment
<!-- Config precedence, environment variables, credential handling -->

### Save irrecoverable secrets BEFORE any subsequent operations
When a setup script generates and registers a secret with an external service (e.g., Circle entity secret), save it to disk **immediately** after the registration API call succeeds — before attempting any further operations. The original `circle_setup.py` registered the entity secret with Circle, then tried to create a wallet (which failed because TEST_API_KEY can't use mainnet chains). The script exited on error without saving the secret. Circle doesn't store entity secrets and has no reset path without the recovery file. Result: permanently locked out of the account. **Pattern:** Any time you generate a secret and send it to a remote service, the very next line must persist it locally. Never gate secret persistence on downstream operations succeeding.

### Circle Programmable Wallets: TEST_API_KEY requires testnet blockchains
Circle TEST_API_KEY keys can only create wallets on testnet blockchains (e.g., `SOL-DEVNET`, `ETH-SEPOLIA`), not mainnet (`SOL`, `ETH`). The API returns HTTP 400 with code 156006. Always check `api_key.startswith("TEST_API_KEY")` and use the corresponding testnet chain. LIVE_API_KEY uses mainnet chains.

### Circle W3S: Destination wallets need an ATA for USDC transfers
When transferring USDC on Solana via Circle W3S, the destination wallet must have an Associated Token Account (ATA) for the USDC token. If it doesn't, Circle's paymaster may refuse with `PAYMASTER_SOL_ATA_CREATION_NOT_ALLOWED`. Fix: fund the destination address with SOL + USDC via faucet (testnet) or ensure it has received USDC before. The `_resolve_chain()` method should auto-map to testnet chains for TEST_API_KEY.

### Bambu access_code vs api_key env vars
Bambu printers use an `access_code` (not the same as an API key). When building env-var config fast paths, don't reuse the same env var (`KILN_PRINTER_API_KEY`) for both `api_key` and `access_code` fields. Use `KILN_PRINTER_ACCESS_CODE` for Bambu access codes. DO NOT fall back to `KILN_PRINTER_API_KEY` — these are semantically different credential types and cross-contamination can cause auth failures or send wrong credentials to wrong backends.

## Hardware / Safety
<!-- Physical printer safety, G-code validation, temperature limits, destructive operations -->

### Preflight checks must be enforced, not optional
If `start_print()` doesn't call `preflight_check()` internally, agents WILL skip it. Safety-critical validation must be mandatory with NO opt-out. The original `skip_preflight=True` parameter was removed entirely — even an "advanced user" bypass is a security hole because agents will discover and use it.

### Path traversal in save/write operations
Any function that accepts a file path from an agent/user and writes to disk is a path traversal risk. Always resolve to absolute path (`os.path.realpath()`), then check it starts with an allowed prefix (home dir, temp dir). Use `tempfile.gettempdir()` resolved through `os.path.realpath()` for cross-platform temp dir detection — macOS `/tmp` resolves to `/private/tmp` and pytest fixtures use `/private/var/folders/`.

### Lock ordering prevents deadlocks
Never emit events (which trigger callbacks) while holding a lock. Callbacks may try to acquire the same lock → deadlock. Pattern: collect event data inside the lock, release the lock, THEN publish events. Applied to `materials.py:deduct_usage()` where `_emit_spool_warnings()` was called inside `with self._lock`.

### Bambu A-series sends UPPERCASE state values
A1/A1 mini printers send `gcode_state` as "RUNNING", "IDLE", "PAUSE" (all caps), unlike X1C/P1S which send lowercase. Always `.lower()` normalize `gcode_state` before matching. Also applies to MQTT `command` field — use case-insensitive comparison for all Bambu string enums.

### Every code path that calls `adapter.start_print()` must run preflight
The `start_print()` MCP tool correctly enforces `preflight_check()`, but composite tools (`slice_and_print`, `download_and_upload`, `generate_and_print`) were calling `adapter.start_print()` directly — bypassing preflight entirely. Always route through the safety gate, even in convenience/shortcut tools. If you add a new tool that starts a print, search for "adapter.start_print" and ensure every call site has a preceding `preflight_check()`.

### Bambu `cancelling` should map to CANCELLING not BUSY
The Bambu adapter mapped `"cancelling"` gcode_state to `PrinterStatus.BUSY` instead of `PrinterStatus.CANCELLING`. Since OctoPrint correctly maps to `CANCELLING`, agents checking for the cancel state got inconsistent behavior across adapters. Always check that new state values map to the most specific enum variant available.

### REST API tier filtering must happen at both listing AND execution
The REST API `_list_tool_schemas()` accepted a `tier` parameter but never used it — all tools were returned regardless. Worse, the tool execution endpoint had no tier check at all. Tier filtering must happen at both the discovery layer (what tools the client sees) AND the execution layer (what tools the client can call). Otherwise tier restrictions are purely cosmetic.

### Use timing-safe comparison for auth tokens
Bearer token comparison in REST API used `!=` which is vulnerable to timing side-channel attacks. Always use `hmac.compare_digest()` for secret/token comparisons. This is a one-line fix that prevents byte-by-byte brute-force attacks.

### Bambu A-series uses implicit FTPS (port 990), not STARTTLS
A1/A1 mini requires implicit TLS on port 990 — the socket must be wrapped in TLS immediately on connect, before the FTP greeting. Standard `ftplib.FTP_TLS` uses explicit STARTTLS (connect plain, then upgrade). Requires a custom `_ImplicitFTP_TLS` subclass that wraps the socket in `connect()` and reuses the TLS session on data channels via `ntransfercmd()`.

### Never auto-print generated or unverified models
3D printers are delicate hardware. Misconfigured or malformed models (especially AI-generated ones) can cause physical damage — jammed nozzles, broken beds, stripped gears. Default to uploading only, require explicit `start_print` call. Provide opt-in toggles (`KILN_AUTO_PRINT_MARKETPLACE`, `KILN_AUTO_PRINT_GENERATED`) rather than opt-out. Surface these settings early in setup so users make a conscious decision.

### Print confirmation requires MQTT polling, not just command success
Sending a print command to Bambu via MQTT succeeds even if the printer doesn't actually start (e.g., wrong file path, lid open). Must poll `gcode_state` via MQTT to confirm the printer transitions to an active state. Without this, `start_print()` returns success while the printer sits idle.

### Auto-recorded outcomes must never overwrite agent-curated data
The scheduler auto-records outcomes on job completion/failure to grow the learning DB passively. Critical design: always check `get_print_outcome(job_id)` before saving — if an agent already recorded a curated outcome (with quality_grade, failure_mode, settings), the auto-recorded version (which lacks these) must not overwrite it. Set `agent_id="scheduler"` to distinguish auto vs curated data. The entire auto-record path must be wrapped in try/except — a persistence failure must never crash the scheduler.

### Preflight advisory checks must never block prints
Learning-database-driven warnings in `preflight_check()` must always set `"passed": True`. If outcome data says a material has 0% success rate on a printer, that's valuable information for the agent — but the decision to proceed must remain with the agent. Mark advisory checks with `"advisory": True` so agents/UIs can distinguish warnings from blocking failures. Also: wrap the entire learning query in try/except so a DB error doesn't break preflight for printers without outcome history.
