# Cron exec pitfalls → safer replacements (portable)

## 1) Command substitution breaks quoting

**Bad (fragile):**
- `TODAY=$(date +%Y-%m-%d)`

**Better:**
- Don’t capture in shell; let a script compute the date.
- Or compute in Python and print JSON/text.

## 2) JSON arguments + nested quotes

**Bad (fragile):**
- `bash -lc '... --meta \'{"lane":"A-fast"}\''` (quotes inside quotes inside quotes)

**Better:**
- Avoid JSON args in shell when you can (omit `--meta`, or use a wrapper script).
- If you must: prefer **double quotes** around the JSON and avoid wrapping the whole command in another quoted `bash -lc '...'.`

## 3) `python3 -c '...'` with list literals / single quotes

A common self-own is:
- `python3 -c '... subprocess.check_output(['openclaw','cron','list',...]) ...'`

This breaks because the inner `['openclaw', ...]` terminates the outer single-quoted `-c` string.

**Better:**
- scripts-first (put the logic in `tools/*.py`)
- or wrap the `-c` string in **double quotes** if you need single quotes inside

## 3.5) Markdown backticks in CLI args (command substitution)
Backticks (`) are **not** just formatting in a shell — they trigger command substitution.

**Bad (fragile):**
- ``--pattern "`‣` / `∙` / `·`"``

This can explode as:
- `sh: 1: ‣: not found`

**Better:**
- Never paste Markdown code formatting into commands.
- If you need to search literal glyphs/odd strings:
  - scripts-first (argv list; no shell)
  - or write the pattern to a file and use `--pattern-file`
  - or add a dedicated helper subcommand (e.g. `grep-md-bullets`) so cron never needs backticks in argv.

## 4) Heredocs in generated shell

**Bad (fragile):**
- `python3 - <<"PY" ... PY` (easy to truncate / misquote)

**Better:**
- Put code in `tools/*.py` and run it.

## 5) `pipefail` + `head`

**Bad:**
- `set -o pipefail; big_command | head`

**Better:**
- Avoid `pipefail` if you’re piping into `head`.
- Or write a script that reads only what it needs.

## 6) Exec packing

**Bad:**
- One huge `bash -lc '...many steps...'`.

**Better:**
- Multiple short exec calls, or one deterministic script.
- Best: a single scripts-first wrapper that runs argv-list subprocess calls (no shell), and `chdir` to repo root.

## 7) `~` expansion and non-interactive shells

Some cron environments do not expand `~` the way you expect.

**Better:**
- Use an absolute path.
- Or use `$HOME` (POSIX) / `%USERPROFILE%` (Windows) if you must reference user-home.

## 8) Tooling optionality (uv/poetry/pip)

Not everyone uses the same Python toolchain.

- If you use **uv**, remember: `-m` is a **python** flag, not a `uv run` flag.
  - **Bad:** `uv run -m my_module`
  - **Good:** `uv run -- python -m my_module`

## 9) Output discipline

- Scheduled jobs should be silent by default: `NO_REPLY`.
- If failure: <= 6 bullets, include *what failed* + *next action*.

## 10) Tool `edit` exact-match footgun

Symptom:
- `Could not find the exact text ... The old text must match exactly including all whitespace and newlines.`

Why it happens:
- Exact-string replacement is brittle under unattended automation (format drift, newline differences, prior edits).

Safer replacement:
- **Don’t use tool `edit` for cron-driven file updates.**
- Use scripts-first patching anchored by headings/markers/substrings (idempotent).
- If you must do a direct replace, **read the file first** and copy the exact old text (including whitespace) into the replace input.

## 11) Secret leakage in debug output
Footgun:
- dumping config files / printing API keys or gateway tokens into logs.

Safer replacement:
- Redact secrets by default.
- When inspecting config, report only whether a key is present (`envref|literal|missing`), never the value.

## 12) Config schema mismatch when copying blocks
Footgun:
- copying a config object from one plugin into another plugin’s config unchanged.

Safer replacement:
- Filter to the destination plugin’s allowed keys (often a minimal `{apiKey, model}` style object).
- Validate by starting the gateway once (or `openclaw doctor`) before relying on the config in cron.
