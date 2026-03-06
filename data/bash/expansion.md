# Parameter Expansion Traps

- `${var:-default}` if unset OR empty — `${var-default}` only if unset
- `${var:=default}` assigns — `${var:-default}` doesn't modify var
- `${var:-$(cmd)}` runs command even if just checking — expansion happens
- `${var: -3}` needs space — without space it's default value syntax
- `${var:0:5}` counts bytes in some locales — not chars
- `${var#pattern}` shortest from start — `##` longest
- `${var%pattern}` shortest from end — `%%` longest
- Pattern is glob, not regex — `*` wildcard, `.` is literal
- `${var/pattern/replace}` first — `//` replaces all
- Empty replacement removes match — `${var//pattern}` deletes all
- `${var^}` uppercase first — `${var^^}` all (bash 4.0+)
- `${!var}` dereferences — value of var named by var
- `${!prefix@}` lists var names with prefix — not values
