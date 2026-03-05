# Project Instructions

## Security Rules (apply to ALL updates)

1. **YAML frontmatter quoting**: All SKILL.md frontmatter values containing colons MUST be double-quoted. The `metadata` field MUST be a single-quoted JSON string (not nested YAML). Test with `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"` before committing.

2. **Sensitive file filtering**: The `_collect_files` function in research.py and `collect_files` in upload.py MUST skip `.env*`, `credentials.json`, `secrets.*`, private keys (`.pem`, `.key`), and auth tokens (`.npmrc`, `.pypirc`, `.netrc`). Never remove this filtering.

3. **WeasyPrint SSRF protection**: The PDF export (`--format pdf`) MUST use a custom `url_fetcher` that blocks all URL fetching. Never pass WeasyPrint an HTML string without this protection -- AI-generated markdown can contain `![](file:///etc/passwd)` or SSRF payloads.

4. **Follow-up sanitization**: The `--follow-up` feature MUST strip all XML-like tags from previous research output before injecting it into the new query. Use `re.sub(r"<[^>]{1,50}>", "", text)` to prevent prompt injection via `<system>`, `<tool_call>`, or delimiter escape attacks.

5. **No API key echo**: Never echo user-provided API keys back to the terminal, even in "helpful" export commands. Use `<your-key>` placeholder instead.

6. **No curl|sh patterns**: Never use `curl ... | sh` install patterns in documentation. Link to official install docs pages instead.

7. **No telemetry**: This project has zero telemetry, analytics, or tracking. Never add any.

## ClawHub Compliance

- The `metadata` field in SKILL.md MUST be a **single-quoted JSON string** (not nested YAML, not unquoted JSON). ClawHub's `getFrontmatterMetadata` calls `JSON.parse()` on string values.
- The JSON MUST include `clawdbot` (not `clawdis`) with: `primaryEnv`, `homepage`, `requires.bins`, `requires.env`, `install`, and `config.requiredEnv`.
- All 6 env vars the code reads MUST be declared in `requires.env`.
- Run `npx clawhub inspect agent-deep-research` after publishing to verify structured data appears.
- The ClawHub security scanner is LLM-based and reads both the SKILL.md content and the registry metadata. Ensure consistency between what the code does and what the metadata declares.

## Testing Checklist (before every release)

1. `python3 -m py_compile scripts/research.py scripts/store.py scripts/upload.py scripts/state.py scripts/onboard.py`
2. `uv run tests/test_cost_estimation.py` (10 tests must pass)
3. `uv run scripts/research.py start "test" --dry-run` (valid JSON on stdout)
4. `uv run scripts/research.py start "test" --context ./scripts --dry-run` (auto-detect python template)
5. `uv run scripts/research.py start "test" --max-cost 0.001` (should abort)
6. `uv run scripts/onboard.py --check` (should show config status)
7. YAML validation: `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`
8. Verify no `curl|sh` patterns: `grep -r 'curl.*install.*sh' scripts/ *.md`
9. Verify sensitive file filter: create a dir with `.env` + `code.py`, run `--context --dry-run`, verify `.env` is skipped

## Release Process

1. Bump version in SKILL.md (inside the metadata JSON string) and scripts/onboard.py
2. Update CHANGELOG.md
3. Run full testing checklist above
4. `git commit && git tag vX.Y.Z && git push origin main --tags`
5. GHA auto-publishes to GitHub Releases + ClawHub + triggers skills.sh re-index
6. After publish: `npx clawhub inspect agent-deep-research` to verify
7. Fix symlink if overwritten: `rm -rf ~/.agents/skills/deep-research && ln -s $(pwd) ~/.agents/skills/deep-research`

## Architecture Notes

- All scripts are PEP 723 standalone (inline metadata, run via `uv run`)
- Dual output convention: stderr = Rich human-readable, stdout = machine-readable JSON
- State file `.gemini-research.json` is local, contains no credentials
- The deep research agent identifier `deep-research-pro-preview-12-2025` is the Interactions API agent name, not a model name
- The default query model in store.py is `gemini-3.1-pro-preview`
