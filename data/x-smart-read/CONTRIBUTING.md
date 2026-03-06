# Contributing

## Adding a New Command

1. Create `scripts/x_yourcommand.py` with the `# /// script` header for `uv run` compatibility
2. Import shared utilities from `x_common.py`:
   ```python
   sys.path.insert(0, str(Path(__file__).resolve().parent))
   from x_common import load_config, get_client, track_usage, budget_warning, check_budget, handle_api_error
   ```
3. Follow existing patterns: argparse CLI, `--dry-run` support, `--force`/`--no-budget` flags
4. Track API costs via `track_usage()` after every API call
5. Show cost footer on all output: `Est. API cost: ~$X.XXX` + `Today's spend: $X.XXX`
6. Use `handle_api_error()` for consistent error messages (401, 402, 403, 429)

## Testing Checklist

Before submitting:

- [ ] `python3 -c "import ast; ast.parse(open('scripts/x_yourscript.py').read())"` — syntax OK
- [ ] `uv run scripts/x_yourscript.py --dry-run ...` — dry run works without API calls
- [ ] Budget check fires correctly (test with budget at $0)
- [ ] `--force` overrides budget block
- [ ] `--no-budget` suppresses all budget warnings
- [ ] Error handling: test with invalid credentials (401), no credits (402)
- [ ] No hardcoded paths — `grep -r "~/.openclaw/workspace" scripts/` returns nothing
- [ ] Config/data files in `.gitignore` — no secrets committed

## PR Process

1. Fork the repo
2. Create a feature branch
3. Add your command + update SKILL.md, AGENTS.md, README.md command table
4. Run the testing checklist above
5. Open a PR with a description of what the command does and its API cost

## Code Style

- Scripts are standalone (each has its own `# /// script` dependencies block)
- Shared code goes in `x_common.py` (no script header — it's imported, not run directly)
- All API costs tracked in `data/usage.json`
- Budget warnings at 50%, 80%, 100% of daily limit
- Plain text output to stdout — no fancy formatting libraries
