# Testing Traps

- `[ $var = "x" ]` fails if var empty — quote: `[ "$var" = "x" ]`
- `[[ ]]` doesn't word-split — `[[ $var = "x" ]]` works unquoted
- `<` and `>` in `[ ]` are redirects — use `-lt`, `-gt` or escape
- Pattern only in `[[ ]]` — `[[ $var == *.txt ]]`
- Pattern must be unquoted — `"*.txt"` matches literal asterisk
- Regex `=~` — don't quote pattern, captures in `BASH_REMATCH`
- `-eq`, `-lt` are numeric — `<`, `>` are lexical string compare
- `[ "10" \< "9" ]` is TRUE — lexical: 1 < 9
- `(( ))` for arithmetic — `(( 10 > 9 ))` cleaner for numbers
- Leading zeros = octal — `08` invalid in arithmetic
- `-e` any type exists — `-f` regular file only
- `-r`, `-w`, `-x` YOUR permissions — not general
- `-L` is symlink — `-f` follows symlink
- Case patterns are globs — `*.txt` works, `.*\.txt` doesn't
