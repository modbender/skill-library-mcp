# Array Traps

- `arr=($(cmd))` splits on spaces — use `mapfile -t arr < <(cmd)`
- Associative arrays need `declare -A` — without it, keys become indices
- `${arr[*]}` joins into single string — `${arr[@]}` preserves elements
- Unquoted `${arr[@]}` splits on spaces — always `"${arr[@]}"`
- `${#arr}` is length of first element — `${#arr[@]}` is count
- `for item in ${arr[@]}` splits — use `"${arr[@]}"`
- `for i in {1..$n}` doesn't expand variable — use `seq` or C-style
- `unset arr[2]` leaves gap — indices don't shift
- `${arr[-1]}` syntax error — use `${arr[@]: -1}` (space required)
- `arr[string]` in indexed array uses 0 — silent wrong behavior
