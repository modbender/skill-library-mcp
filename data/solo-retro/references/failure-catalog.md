# Failure Catalog — Known Pipeline Failure Patterns

Reference for `/retro` skill. Each pattern has a signature to look for in logs, root cause analysis, and a concrete fix.

## Pattern 1: Unknown Skill Name

**Signature in logs:**
- `Unknown skill: {name}` in progress.md or iter logs
- INVOKE line shows wrong skill name (e.g., `build` instead of `/solo:build`)
- Multiple consecutive iterations on same stage with `continuing` result

**Root cause:** Skill invoked without `/solo:` prefix or with wrong name. The `name:` field in SKILL.md frontmatter must match the plugin invocation pattern. Pipeline calls `/solo:{name}`, so SKILL.md must have `name: solo-{name}`.

**Impact:** Every failed iteration is 100% wasted — Claude starts a session, can't find the skill, and exits.

**Fix options:**
1. Fix SKILL.md `name:` field to use `solo-` prefix (e.g., `name: solo-review` not `name: review`)
2. Republish plugin: `cd solo-factory && make plugin-publish`
3. Verify with: `claude skill list | grep solo`

**Prevention:** Add pre-flight skill name check to `solo-dev.sh` — verify skill exists before entering main loop.

## Pattern 2: Signal Missing (Spin-Loop)

**Signature in logs:**
- Same stage appears N consecutive times (N > 3) in STAGE lines
- All iterations show `result: continuing` (no `stage complete`)
- No `<solo:done/>` in corresponding iter logs
- Eventually hits MAXITER

**Root cause:** The skill completed its work but didn't output the `<solo:done/>` signal tag. Could be:
- Signal instruction truncated (long output hit context limit)
- Skill output the tag in a code block (bash grep doesn't match inside code blocks)
- Skill errored before reaching signal phase
- `--print` output format issue (stream-json may wrap text differently)

**Impact:** Burns all remaining iterations until max_iterations ceiling.

**Fix options:**
1. Add signal reminder earlier in skill (not just at end of prompt)
2. Check if skill has `<solo:done/>` in its SKILL.md instructions
3. Add circuit breaker to `solo-dev.sh` (consecutive failure detection)

**Prevention:** Circuit breaker in `solo-dev.sh` — abort after N consecutive failures for same stage.

## Pattern 3: Max-Iter Burn

**Signature in logs:**
- `MAXITER | Reached max iterations (N)` line present
- Often combined with Pattern 2 (spin-loop causing the burn)

**Root cause:** No circuit breaker — pipeline retries to max even when same error repeats. Default `max_iterations=15` is generous enough for normal pipelines but burns fast on spin-loops.

**Impact:** Time and API cost wasted on hopeless retries.

**Fix options:**
1. Add consecutive-failure detection to main loop in `solo-dev.sh`
2. Lower `max_iterations` for known-safe pipelines
3. Use `--from` flag to skip problematic stages on restart

**Prevention:** Circuit breaker (5 consecutive failures → abort with CIRCUIT log tag).

## Pattern 4: Doubled Signal

**Signature in logs:**
- `<solo:done/><solo:done/>` or `<solo:done/>` appears twice in same iter log
- SIGNAL line appears twice for same iteration

**Root cause:** Agent outputs the tag, then repeats it in a summary or closing statement. Bash `grep -q` only checks existence (not count), so this is harmless.

**Impact:** None — purely cosmetic. No wasted iterations.

**Fix:** No fix needed. Note in retro report but don't penalize.

## Pattern 5: Redo Loop

**Signature in logs:**
- Pattern: STAGE build → STAGE review → SIGNAL `<solo:redo/>` → STAGE build → STAGE review (repeating)
- More than 3 build→review cycles for the same plan track

**Root cause:** Review keeps finding issues that build can't fix within one iteration. Common causes:
- Acceptance criteria too strict for automated build
- Review checks things that weren't in the plan
- Flaky tests causing review to fail intermittently

**Impact:** Each redo cycle costs 2+ iterations (build + review minimum).

**Fix options:**
1. Cap redo cycles at 3 in `solo-dev.sh` (after 3 redos, force `<solo:done/>` on review)
2. Improve plan granularity so build can complete criteria in fewer iterations
3. Add `--max-redo` flag to pipeline

**Prevention:** Redo counter in `solo-dev.sh` — after N redos for same plan track, log warning and continue.

## Pattern 6: Plan Not Found

**Signature in logs:**
- `PLAN | Active plan track:` line present but no spec.md found
- Build stage runs but produces no useful work
- `CHECK | plan | ... -> NOT FOUND`

**Root cause:** Plan directory exists but files are missing, or glob pattern doesn't match the actual file structure.

**Impact:** Build stage runs blind without plan context.

**Fix options:**
1. Check `docs/plan/*/*.md` glob pattern matches actual structure
2. Verify `/plan` skill created both `spec.md` and `plan.md`
3. Check for case-sensitivity issues in directory names

**Prevention:** Add plan file existence check before build stage in `solo-dev.sh`.

## Pattern 7: CWD Mismatch

**Signature in logs:**
- Skill tries to read files from wrong directory
- `No such file or directory` errors in iter logs
- Scaffold runs from project dir instead of KB dir (or vice versa)

**Root cause:** `solo-dev.sh` manages CWD switching (KB dir for scaffold, project dir for everything else). If project root detection fails, all subsequent stages run from wrong directory.

**Impact:** Skills can't find project files, producing errors.

**Fix options:**
1. Verify `project_root` in state YAML matches actual project location
2. Check CWD log entries match expectations
3. Ensure `~/startups/active/{project}` exists before starting non-scaffold stages

## Pattern 8: MCP Connection Failure

**Signature in logs:**
- `MCP server connection failed` or `tool not found` in iter logs
- Skills fall back to Glob/Grep (slower, less context)
- No `mcp__solograph__` tool calls in iter logs

**Root cause:** MCP server (solograph) failed to start or crashed during pipeline. Common with long-running pipelines — memory pressure from multiple Claude sessions.

**Impact:** Skills still work (MCP is optional) but with reduced context and speed.

**Fix options:**
1. Restart MCP server: kill existing process, let next `claude` invocation restart it
2. Check `~/.mcp.json` configuration is valid
3. Monitor memory during pipeline (solograph + MLX can be memory-hungry)
