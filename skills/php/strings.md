# String Traps

- Encoding hell — `strlen()` counts bytes not chars, `mb_strlen()` for UTF-8
- `strpos()` returns 0 — `if(strpos(...))` fails when found at start, use `!== false`
- Single vs double quotes — `"$var"` interpolates, `'$var'` is literal
- Heredoc indentation — closing identifier must not be indented (PHP <7.3)
- Regex delimiters — `/pattern/` or `#pattern#`, forgetting causes error
- `preg_replace` with `/e` — removed in PHP 7, was code injection vector
- Null byte — `"file\0.txt"` truncates at null in some functions
