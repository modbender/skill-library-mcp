# Gate: Adversarial Red-Team

**Question:** Can an attacker break, bypass, or exploit this code?

Run `scripts/red-team.sh [path]` first. Then manually review the findings.

---

## Categories

### 1. Injection Attacks

Check for **SQL injection:**
- String concatenation in queries (`"SELECT * FROM " + userInput`)
- f-strings or template literals building raw SQL
- Missing parameterized queries

Check for **Command injection:**
- `exec()`, `eval()`, `spawn()`, `popen()`, `system()` with user input
- Shell=True in subprocess calls
- Unescaped user data in shell commands

Check for **Path traversal:**
- `../`, `%2e%2e%2f`, `..%5c` in file path construction
- Missing path normalization before file operations
- File reads/writes using user-supplied filenames without validation

Check for **Template injection:**
- User input rendered directly in templates (Jinja2, Handlebars, etc.)
- `render(template=userInput)` patterns
- Unsafe `eval` of template strings

Check for **XSS (if web-facing):**
- Unescaped user input in HTML responses
- `innerHTML = userInput` patterns
- Missing Content-Security-Policy headers

### 2. Authentication & Authorization Bypasses

Check for:
- Routes/endpoints without auth middleware applied
- Auth checks that can be bypassed by changing HTTP method
- JWT algorithms set to `none`
- Hardcoded credentials or API keys in source
- Secrets in environment variable names visible in error messages
- Missing rate limiting on auth endpoints
- Predictable session tokens or reset tokens

### 3. Race Conditions & TOCTOU

Check for:
- Time-Of-Check-Time-Of-Use (check file exists, then use it — window in between)
- Non-atomic read-modify-write operations on shared state
- Double-spend patterns (balance checked, then decremented in separate operations)
- Missing database transactions around multi-step operations
- File operations without locking

### 4. Input Abuse

Test with adversarial inputs:
- **Null bytes**: `\x00` in strings (can truncate strings in some languages)
- **Unicode attacks**: Homoglyph substitution, overlong UTF-8, RTL override characters
- **Oversized payloads**: Empty string, single char, 1MB string, 1GB string
- **Negative/boundary numbers**: -1, 0, MAX_INT, MIN_INT, NaN, Infinity
- **Type confusion**: Pass string where int expected, array where string expected
- **Empty collections**: Empty array, empty object, null vs undefined
- **Special characters**: `'`, `"`, `;`, `\n`, `\r\n`, `\0`, `<`, `>`, `&`

### 5. Resource Exhaustion

Check for:
- **Regex DoS (ReDoS)**: Exponential-time regexes on user input (`(a+)+`, `([a-zA-Z]+)*`)
- **Recursive structures**: Missing depth limits on recursive parsing/traversal
- **Memory bombs**: Allocating large buffers based on user-controlled size
- **Zip bombs**: Compressed files expanded without size limits
- **Infinite loops**: User input that can cause loops to never terminate
- **File descriptor exhaustion**: Opening files without closing them in error paths

### 6. Cryptographic Weaknesses

Check for:
- Weak algorithms: MD5, SHA1 for security purposes, DES, 3DES, RC4
- ECB mode block cipher usage
- Hardcoded IVs or nonces
- Predictable random number generation (`Math.random()`, `rand()` for security)
- Missing certificate validation (`verify=False`, `checkServerIdentity: () => {}`)
- Passwords stored as plain text or weak hash (MD5/SHA1)
- Timing attacks in credential comparison (use constant-time compare)

### 7. Error Handling & Information Leaks

Check for:
- Stack traces returned to clients in production
- Verbose error messages exposing internal paths, DB schemas, library versions
- Exception handlers that swallow errors silently
- Debug modes left on in production config
- Sensitive data (passwords, tokens, PII) in log output
- Missing error handling in async code (unhandled promise rejections)

### 8. Deserialization & Prototype Pollution

Check for:
- Unsafe deserialization: `pickle.loads(userInput)`, `YAML.load(userInput)` (vs `safe_load`)
- `JSON.parse` on untrusted input fed directly to eval
- Prototype pollution: `Object.assign({}, userInput)` where keys aren't validated
- `__proto__`, `constructor`, `prototype` keys in user-controlled objects
- Node.js `require()` with user-controlled paths

---

## Pass/Fail Criteria

| Finding | Severity | Effect on Verdict |
|---------|----------|------------------|
| SQL/Command/Path injection | BLOCKER | Blocked 🚫 |
| Auth bypass | BLOCKER | Blocked 🚫 |
| Hardcoded secret in source | BLOCKER | Blocked 🚫 |
| Unsafe deserialization | BLOCKER | Blocked 🚫 |
| ReDoS with user input | BLOCKER | Blocked 🚫 |
| Weak crypto for security | WARNING | Caution ⚠️ |
| Info leak in errors | WARNING | Caution ⚠️ |
| Missing rate limiting | WARNING | Caution ⚠️ |
| Race condition | WARNING | Caution ⚠️ |
| TOCTOU | WARNING | Caution ⚠️ |
| Debug flag on | INFO | Note only |
| Missing input validation | Depends on context | BLOCKER if injection possible, WARNING otherwise |

**Pass:** Zero BLOCKER findings  
**Caution:** WARNING findings only, no BLOCKERs  
**Fail/Blocked:** Any BLOCKER finding

---

## Script Output

`scripts/red-team.sh [path]` outputs:
```json
{
  "project": "/path/to/project",
  "findings": [
    {
      "id": "SQL_CONCAT",
      "category": "injection",
      "pattern": "SQL string concatenation",
      "severity": "blocker",
      "file": "src/db.js",
      "line": 42,
      "evidence": "query = \"SELECT * FROM users WHERE id = \" + userId",
      "recommendation": "Use parameterized queries"
    }
  ],
  "summary": {
    "total": 3,
    "blockers": 1,
    "warnings": 2,
    "info": 0
  },
  "verdict": "FAIL"
}
```
