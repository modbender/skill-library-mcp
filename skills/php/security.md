# Security Traps

- SQL injection — use prepared statements, NEVER concatenate user input
- XSS — `htmlspecialchars($input, ENT_QUOTES, 'UTF-8')` on all output
- CSRF — verify token on state-changing requests
- File upload — check MIME type, extension, AND magic bytes
- `include($userInput)` — remote file inclusion, validate path strictly
- `unserialize()` — can execute code, use `json_decode()` instead
- `extract($_POST)` — overwrites variables, including `$isAdmin`
- Session fixation — `session_regenerate_id(true)` on login
- Weak comparison in auth — `"0e123" == "0e456"` is true, breaks hash compare
