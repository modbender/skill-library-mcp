# Security Remediation Guide

Step-by-step guidance for fixing security issues detected by obekt-security.

## Critical Issues - Immediate Action Required

### Command Injection

**Problem:** User input is directly passed to system commands.

**Fix Strategies:**

1. **Use parameterized commands**
```python
# BAD
os.system(f"ls {user_path}")

# GOOD - subprocess with args list
import subprocess
subprocess.run(["ls", user_path], check=True)
```

2. **Never use shell=True with user input**
```python
# BAD
subprocess.call(f"cat {file_path}", shell=True)

# GOOD
subprocess.run(["cat", file_path])
```

3. **Validate and sanitize all paths**
```python
import os
import subprocess

def safe_command_run(path):
    # Validate path is within allowed directory
    allowed_dir = "/var/data"
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(allowed_dir):
        raise ValueError("Path outside allowed directory")

    subprocess.run(["cat", abs_path], check=True)
```

---

### SQL Injection

**Problem:** SQL queries constructed with string concatenation or f-strings.

**Fix Strategies:**

1. **Use parameterized queries**
```python
# BAD
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

2. **Use ORM libraries**
```python
from sqlalchemy import text
from sqlalchemy.orm import Session

# Good - SQLAlchemy parameterized
session.execute(
    text("SELECT * FROM users WHERE id = :id"),
    {"id": user_id}
)
```

3. **Use query builders**
```python
# Good - Django ORM
users = User.objects.filter(id=user_id)
```

---

### Hardcoded Cryptographic Secrets

**Problem:** Private keys, mnemonics, wallet seeds in code.

**Fix Strategies:**

1. **Use environment variables**
```python
import os
from eth_account import Account

# BAD - Never hardcode
private_key = "0xabc123456789..."

# GOOD - Load from environment
private_key = os.getenv('WALLET_PRIVATE_KEY')
if not private_key:
    raise ValueError("WALLET_PRIVATE_KEY not set")
account = Account.from_key(private_key)
```

2. **Use secret management services**
```python
import boto3
import base64

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return base64.b64decode(response['SecretBinary'])
```

3. **Never commit secrets to version control**
```bash
# Add to .gitignore
.env
*.key
*.pem
secrets.yaml
```

4. **Rotate credentials if they were ever exposed**
- Immediately revoke exposed keys
- Generate new credentials
- Update all services
- Investigate potential compromise timeline

---

## High Issues - Priority Fixes

### Hardcoded API Keys and Tokens

**Problem:** Service credentials hardcoded in source code.

**Fix Strategies:**

1. **Environment variables**
```python
# .env file (NEVER commit)
STRIPE_API_KEY=sk_live_51AbCdEf...
GITHUB_TOKEN=ghp_abc123...

# Python code
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv('STRIPE_API_KEY')
```

2. **Secret management**
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

3. **Runtime secrets loading**
```python
def load_config():
    return {
        'api_key': os.getenv('API_KEY'),
        'database_url': os.getenv('DATABASE_URL'),
    }
```

---

### Weak Cryptography

**Problem:** Using broken or weak cryptographic algorithms.

**Fix Strategies:**

1. **Hashing - Use modern algorithms**
```python
# BAD - Broken
import hashlib
hashlib.md5(password.encode()).hexdigest()
hashlib.sha1(password.encode()).hexdigest()

# GOOD - Modern
import hashlib
hashlib.sha256(password.encode()).hexdigest()

# BETTER - For passwords
import bcrypt
bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

2. **Encryption - Use strong ciphers**
```python
# BAD - Broken
from Crypto.Cipher import DES
from Crypto.Cipher import RC4

# GOOD - AES-256-GCM
from Crypto.Cipher import AES

def encrypt_aes_gcm(key, plaintext, nonce):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return ciphertext, tag
```

3. **Key management**
- Never hardcode encryption keys
- Use key derivation functions (KDFs)
- Rotate keys periodically

---

### Path Traversal

**Problem:** User-controlled paths can escape allowed directories.

**Fix Strategies:**

1. **Validate and restrict paths**
```python
import os

def safe_open(user_path, base_dir="/var/data"):
    # Get absolute paths
    abs_base = os.path.abspath(base_dir)
    abs_user = os.path.abspath(os.path.join(abs_base, user_path))

    # Ensure path is within base directory
    if not abs_user.startswith(abs_base):
        raise ValueError("Path traversal attempt detected")

    # Get just the filename (prevent ../)
    filename = os.path.basename(user_path)
    safe_path = os.path.join(abs_base, filename)

    return open(safe_path, 'r')
```

2. **Use whitelists for allowed operations**
```python
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.png', '.jpg'}

def safe_upload(file_path, content):
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("File type not allowed")
    # Proceed with upload
```

3. **Sanitize filenames**
```python
import re

def sanitize_filename(filename):
    # Remove path separators and dangerous characters
    clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
    clean = clean.strip('. ')
    return clean
```

---

### Weak Random Numbers

**Problem:** Using predictable random number generators for security.

**Fix Strategies:**

1. **Cryptographic random - use secrets module**
```python
# BAD - Predictable
import random
token = random.randint(100000, 999999)

# GOOD - Cryptographically secure
import secrets
token = secrets.randbelow(1000000)
```

2. **For session tokens**
```python
# BAD
import random
session_id = ''.join(random.choice('0123456789') for _ in range(10))

# GOOD
import secrets
session_id = secrets.token_hex(16)
```

3. **For API keys**
```python
import secrets

def generate_api_key():
    return secrets.token_urlsafe(32)
```

4. **For crypto wallet operations**
```python
from eth_account import Account

# Good - Uses cryptographic randomness
account = Account.create()
private_key = account.key.hex()
```

---

## Medium Issues - Important Fixes

### Information Leakage in Logs

**Problem:** Sensitive data logged to console or files.

**Fix Strategies:**

1. **Remove sensitive data from logs**
```python
# BAD
logging.info(f"User login: {email}, password: {password}")

# GOOD
logging.info(f"User login: {email}")
```

2. **Use appropriate log levels**
```python
# DEBUG: Detailed info (disabled in production)
logging.debug(f"API call: {api_key[:8]}...")

# INFO: General operational info
logging.info(f"User {user_id} logged in successfully")

# ERROR: Errors with context (no secrets)
logging.error(f"Authentication failed for user {email}")
```

3. **Don't log full secrets**
```python
# BAD
logger.info(f"Using API key: {api_key}")

# GOOD
logger.info(f"Using API key: {api_key[:8]}...***")
```

---

### Unsafe Redirects

**Problem:** Redirect URLs controlled by user input.

**Fix Strategies:**

1. **Redirect to allowlisted domains**
```python
ALLOWED_REDIRECTS = {'/dashboard', '/profile', '/settings'}

def safe_redirect(user_url):
    parsed = urlparse(user_url)
    path = parsed.path

    if path in ALLOWED_REDIRECTS:
        return redirect(path)
    else:
        return redirect('/home')  # Default safe location
```

2. **Use same-origin policy**
```python
import urllib.parse

def safe_redirect(url):
    # Ensure redirect is to same domain
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != request.host:
        return redirect('/')
    return redirect(url)
```

---

### Missing Input Validation

**Problem:** No validation of user input.

**Fix Strategies:**

1. **Use input validation libraries**
```python
from pydantic import BaseModel, validator

class UserData(BaseModel):
    email: str
    age: int

    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('must contain "@"')
        return v

    @validator('age')
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('age must be positive')
        return v
```

2. **Validate types and ranges**
```python
def safe_int_input(value, min_val=0, max_val=100):
    try:
        num = int(value)
        return min(max(num, min_val), max_val)
    except ValueError:
        raise ValueError("Invalid number")
```

3. **Sanitize strings**
```python
import re

def sanitize_string(text, max_length=100):
    # Remove dangerous characters
    clean = re.sub(r'[<>"\'&;]', '', text)
    # Truncate to max length
    return clean[:max_length]
```

---

## After Remediation

### Testing

1. **Run security scans again**
   ```bash
   python3 scripts/threat_scan.py --severity high
   python3 scripts/secret_scan.py
   ```

2. **Manual code review**
   - Check all user input paths
   - Verify secrets are removed
   - Validate external dependencies

3. **Test edge cases**
   - Empty inputs
   - Very long inputs
   - Special characters (`../`, `\x00`, `<script>`)

### Verification

- [ ] All critical issues resolved
- [ ] All high issues resolved
- [ ] Medium issues documented/risk accepted
- [ ] Secrets removed from repository
- [ ] Environment variables documented
- [ ] Tests pass for edge cases
- [ ] Security scan returns clean results

### Documentation

Update README.md with:
- Security considerations
- Required environment variables
- Deployment security checklist
- Incident response procedures

---

## Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CWE/SANS Top 25**: https://cwe.mitre.org/top25/
- **Python security best practices**: https://python.readthedocs.io/en/stable/library/secrets.html
- **Crypto standards**: NIST Special Publication 800-38A
