# Error Handling Traps

- `set -e` doesn't trigger in `if` condition — `if ! cmd; then` is safe
- `set -e` doesn't trigger after `||` or `&&` — `cmd || true` is safe
- `$(cmd)` in assignment doesn't trigger -e — subshell error not propagated
- Exit code is last command only — `bad | good` returns 0
- `set -o pipefail` fails if ANY fails — but can't tell which
- `${PIPESTATUS[@]}` has all exit codes — check after pipeline
- Pipe creates subshell — variables set inside don't persist
- `( )` is subshell — variables don't escape
- `$( )` captures stdout only — stderr goes to terminal
- `exit` in subshell only exits subshell — parent continues
- `trap cleanup EXIT` runs on ANY exit — including errors
- `return` in non-function is error — use `exit` at top level
- `command 2>&1` order matters — `2>&1 >file` wrong, `>file 2>&1` right
