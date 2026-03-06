---
name: Bash
slug: bash
version: 1.0.2
description: Write reliable Bash scripts with proper quoting, error handling, and parameter expansion.
metadata: {"clawdbot":{"emoji":"🖥️","requires":{"bins":["bash"]},"os":["linux","darwin"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Arrays and loops | `arrays.md` |
| Parameter expansion | `expansion.md` |
| Error handling patterns | `errors.md` |
| Testing and conditionals | `testing.md` |

## Quoting Traps

- Always quote variables—`"$var"` not `$var`, spaces break unquoted
- `"${arr[@]}"` preserves elements—`${arr[*]}` joins into single string
- Single quotes are literal—`'$var'` doesn't expand
- Quote command substitution—`"$(command)"` not `$(command)`

## Word Splitting and Globbing

- Unquoted `$var` splits on whitespace—`file="my file.txt"; cat $file` fails
- Unquoted `*` expands to files—quote or escape if literal: `"*"` or `\*`
- `set -f` disables globbing—or quote everything properly

## Test Brackets

- `[[ ]]` preferred over `[ ]`—no word splitting, supports `&&`, `||`, regex
- `[[ $var == pattern* ]]`—glob patterns without quotes on right side
- `[[ $var =~ regex ]]`—regex match, don't quote the regex
- `-z` is empty, `-n` is non-empty—`[[ -z "$var" ]]` tests if empty

## Subshell Traps

- Pipes create subshells—`cat file | while read; do ((count++)); done`—count lost
- Use `while read < file` or process substitution—`while read; do ...; done < <(command)`
- `( )` is subshell, `{ }` is same shell—variables in `( )` don't persist

## Exit Handling

- `set -e` exits on error—but not in `if`, `||`, `&&` conditions
- `set -u` errors on undefined vars—catches typos
- `set -o pipefail`—pipeline fails if any command fails, not just last
- `trap cleanup EXIT`—runs on any exit, even errors

## Arrays

- Declare: `arr=(one two three)`—or `arr=()` then `arr+=(item)`
- Length: `${#arr[@]}`—not `${#arr}`
- All elements: `"${arr[@]}"`—always quote
- Indices: `${!arr[@]}`—useful for sparse arrays

## Parameter Expansion

- Default value: `${var:-default}`—use default if unset/empty
- Assign default: `${var:=default}`—also assigns to var
- Error if unset: `${var:?error message}`—exits with message
- Substring: `${var:0:5}`—first 5 chars
- Remove prefix: `${var#pattern}`—`##` for greedy

## Arithmetic

- `$(( ))` for math—`result=$((a + b))`
- `(( ))` for conditions—`if (( count > 5 )); then`
- No `$` needed inside `$(( ))`—`$((count + 1))` not `$(($count + 1))`

## Common Mistakes

- `[ $var = "value" ]` fails if var empty—use `[ "$var" = "value" ]` or `[[ ]]`
- `if [ -f $file ]` with spaces—always quote: `if [[ -f "$file" ]]`
- `local` in functions—without it, variables are global
- `read` without `-r`—backslashes interpreted as escapes
- `echo` portability—use `printf` for reliable formatting
