# Platform support (Windows, macOS, Linux)

clawd-migrate is written to work on **Windows**, **macOS** (Terminal, iTerm2), and **Linux**. Below are the main compatibility choices (no manual testing was done on macOS from this repo; these are code-level guarantees).

## Paths

- All path handling uses **pathlib.Path** so `/` vs `\` is correct per OS.
- **Path.expanduser()** is used for `~` (works on all three).
- No hardcoded backslashes or drive letters.

## Python

- **Bin script (Node):** On Windows it runs `python`; on macOS/Linux it tries `python3` then `python` so the right interpreter is used.
- **Tests (npm test):** Same: `python3` on Unix, `python` on Windows.

## Subprocess (openclaw setup)

- **shell=True** is used for `npm install -g openclaw` and `openclaw onboard` on all platforms so the same **PATH** as the user’s terminal is used (important on macOS where npm/openclaw may be in `/usr/local/bin` or an nvm path).
- **cwd** is passed as `str(target_dir)` so the correct path form is used per OS.

## ANSI colors

- The TUI uses standard ANSI escape codes; they work in:
  - **Windows:** Windows Terminal, PowerShell 7+.
  - **macOS:** Terminal.app, iTerm2.
  - **Linux:** Most terminal emulators.

## Encoding

- No Unicode in banner or prompts that would break **cp1252** (Windows) or **UTF-8** (macOS/Linux); the lobster art is ASCII.

## macOS-specific

- **python3** is the default when running from the npm-installed bin and when running `npm test`.
- Global npm bins (e.g. `openclaw`) are found via the shell’s PATH when using the “install openclaw and onboard” step.

If you hit issues on macOS Terminal, checking PATH (`echo $PATH`) and that `python3` and `npm` are available is a good first step.
