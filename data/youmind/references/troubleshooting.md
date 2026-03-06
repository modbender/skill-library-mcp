# Youmind Skill Troubleshooting

## Quick Fixes

| Issue | Fix |
|---|---|
| `ModuleNotFoundError` | Use `python scripts/run.py ...` instead of direct script call |
| Redirected to sign-in during query | Run `python scripts/run.py auth_manager.py setup` |
| No chat input found | Retry with `--show-browser` and update selectors in `scripts/config.py` |
| Timeout waiting for answer | Ask a shorter question or increase selector wait logic |
| `ProcessSingleton` / `SingletonLock` error | Close stuck Chrome/skill process and retry (skill now auto-cleans stale lock and retries once) |
| Board not found | `python scripts/run.py board_manager.py list` |

## Authentication Problems

```bash
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py validate
python scripts/run.py auth_manager.py reauth
```

If validation fails repeatedly:

```bash
python scripts/run.py auth_manager.py clear
python scripts/run.py auth_manager.py setup
```

## Browser Issues

If browser hangs:

```bash
pkill -f chrome
python scripts/run.py cleanup_manager.py --confirm --preserve-library
python scripts/run.py auth_manager.py setup
```

If you still see profile lock errors:

```bash
rm -f data/browser_state/browser_profile/SingletonLock
rm -f data/browser_state/browser_profile/SingletonCookie
rm -f data/browser_state/browser_profile/SingletonSocket
```

## Selector Drift (Most Common)

Youmind UI updates can break selectors.

Files to edit:
- `scripts/config.py`: `QUERY_INPUT_SELECTORS`, `RESPONSE_SELECTORS`, `THINKING_SELECTORS`, `SEND_BUTTON_SELECTORS`

Debug command:

```bash
python scripts/run.py ask_question.py --question "test" --board-url "https://youmind.com/boards/..." --show-browser
```

## Full Reset

```bash
python scripts/run.py cleanup_manager.py --confirm --force
rm -rf .venv
python scripts/run.py auth_manager.py setup
```

Then re-add boards:

```bash
python scripts/run.py board_manager.py add --url ... --name ... --description ... --topics ...
```
