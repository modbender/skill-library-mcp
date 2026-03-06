# SurrealDB Security

SurrealDB has a layered security model built into the database itself, eliminating the need for separate middleware or application-level permission checks in many cases. Authentication, authorization, and row-level security are all defined in SurrealQL and enforced by the database engine.

---

## Authentication Hierarchy

SurrealDB uses a four-level authentication hierarchy. Each level has access to its scope and everything beneath it.

```
Root User
  |-- Full system access (all namespaces, databases, tables)
  |
  +-- Namespace User
       |-- Access to all databases within a namespace
       |
       +-- Database User
            |-- Access to all tables within a database
            |
            +-- Record User
                 |-- Access governed by table PERMISSIONS
                 |-- Authenticated via DEFINE ACCESS ... TYPE RECORD
```

### Root Users

Root users have unrestricted access to the entire SurrealDB instance. Use them only for administrative operations.

```surrealql
-- Define a root user (requires existing root access)
DEFINE USER admin ON ROOT PASSWORD 'strong-password-here' ROLES OWNER;
DEFINE USER operator ON ROOT PASSWORD 'another-password' ROLES EDITOR;
DEFINE USER readonly ON ROOT PASSWORD 'readonly-pass' ROLES VIEWER;

-- Roles:
-- OWNER: full control (create/drop namespaces, manage users)
-- EDITOR: read/write data, manage schemas
-- VIEWER: read-only access
```

### Namespace Users

Namespace users can access all databases within their namespace but cannot access other namespaces.

```surrealql
USE NS production;

DEFINE USER ns_admin ON NAMESPACE PASSWORD 'ns-password' ROLES OWNER;
DEFINE USER ns_dev ON NAMESPACE PASSWORD 'dev-password' ROLES EDITOR;
DEFINE USER ns_reader ON NAMESPACE PASSWORD 'reader-pass' ROLES VIEWER;
```

### Database Users

Database users can access tables and data within a single database.

```surrealql
USE NS production DB app_main;

DEFINE USER db_admin ON DATABASE PASSWORD 'db-password' ROLES OWNER;
DEFINE USER db_writer ON DATABASE PASSWORD 'writer-pass' ROLES EDITOR;
DEFINE USER db_reader ON DATABASE PASSWORD 'reader-pass' ROLES VIEWER;
```

### Record Users

Record users are end-user accounts authenticated via `DEFINE ACCESS ... TYPE RECORD`. They are the most granular level and are subject to table-level PERMISSIONS clauses.

```surrealql
-- See DEFINE ACCESS section below for full details
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP (CREATE user SET email = $email, pass = crypto::argon2::generate($pass))
    SIGNIN (SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass))
    DURATION FOR TOKEN 15m, FOR SESSION 12h;
```

---

## DEFINE ACCESS

The `DEFINE ACCESS` statement configures how users authenticate with SurrealDB. There are three access types: RECORD, JWT, and API KEY.

### Record-Based Authentication (End Users)

Record access allows end users to sign up and sign in. The `SIGNUP` and `SIGNIN` clauses define SurrealQL expressions that execute during authentication.

```surrealql
-- Basic email/password authentication
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP (
        CREATE user SET
            email = $email,
            pass = crypto::argon2::generate($pass),
            created_at = time::now(),
            role = 'member'
    )
    SIGNIN (
        SELECT * FROM user
        WHERE email = $email
        AND crypto::argon2::compare(pass, $pass)
    )
    DURATION FOR TOKEN 15m, FOR SESSION 12h;
```

After successful authentication, `$auth` contains the authenticated user record and `$access` contains the access method name. These are available in PERMISSIONS clauses.

```surrealql
-- Advanced record access with validation
DEFINE ACCESS secure_account ON DATABASE TYPE RECORD
    SIGNUP (
        -- Validate email format
        IF string::is::email($email) THEN
            CREATE user SET
                email = string::lowercase($email),
                pass = crypto::argon2::generate($pass),
                name = $name,
                created_at = time::now(),
                verified = false,
                role = 'member'
        ELSE
            THROW "Invalid email format"
        END
    )
    SIGNIN (
        SELECT * FROM user
        WHERE email = string::lowercase($email)
        AND crypto::argon2::compare(pass, $pass)
    )
    DURATION FOR TOKEN 15m, FOR SESSION 12h;
```

```surrealql
-- Multi-tenant record access
DEFINE ACCESS tenant_account ON DATABASE TYPE RECORD
    SIGNUP (
        -- Verify tenant exists before creating user
        LET $tenant = SELECT * FROM tenant WHERE id = $tenant_id;
        IF count($tenant) > 0 THEN
            CREATE user SET
                email = $email,
                pass = crypto::argon2::generate($pass),
                tenant = $tenant_id,
                role = 'member'
        ELSE
            THROW "Invalid tenant"
        END
    )
    SIGNIN (
        SELECT * FROM user
        WHERE email = $email
        AND crypto::argon2::compare(pass, $pass)
    )
    DURATION FOR TOKEN 30m, FOR SESSION 24h;
```

### JWT-Based Authentication

JWT access allows external identity providers to authenticate users with SurrealDB.

```surrealql
-- HMAC-based JWT (symmetric key)
DEFINE ACCESS jwt_auth ON DATABASE TYPE JWT
    ALGORITHM HS256
    KEY 'your-256-bit-secret-key-here'
    DURATION FOR TOKEN 1h;

-- RSA-based JWT (asymmetric key, more secure)
DEFINE ACCESS jwt_rsa ON DATABASE TYPE JWT
    ALGORITHM RS256
    KEY '-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----'
    DURATION FOR TOKEN 1h;

-- ECDSA-based JWT
DEFINE ACCESS jwt_ecdsa ON DATABASE TYPE JWT
    ALGORITHM ES256
    KEY '-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcD...
-----END PUBLIC KEY-----'
    DURATION FOR TOKEN 1h;

-- JWT with record binding (map JWT claims to a user record)
DEFINE ACCESS external_auth ON DATABASE TYPE RECORD
    WITH JWT ALGORITHM RS256 KEY '-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----'
    DURATION FOR TOKEN 1h;
```

### Supported JWT Algorithms

| Algorithm | Type | Key |
|---|---|---|
| HS256, HS384, HS512 | HMAC (symmetric) | Shared secret key |
| RS256, RS384, RS512 | RSA (asymmetric) | Public key for verification |
| ES256, ES384, ES512 | ECDSA (asymmetric) | Public key for verification |
| PS256, PS384, PS512 | RSA-PSS (asymmetric) | Public key for verification |
| EdDSA | EdDSA (asymmetric) | Public key for verification |

### API Key Authentication

```surrealql
-- Define API key access
DEFINE ACCESS api_access ON DATABASE TYPE API KEY;

-- API keys are generated and managed through the SurrealDB API
-- They provide simple bearer token authentication
```

### Token Duration Configuration

```surrealql
-- Duration controls how long tokens and sessions last
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP (...)
    SIGNIN (...)
    -- Token: short-lived, used for individual requests
    -- Session: longer-lived, maintains authenticated state
    DURATION FOR TOKEN 15m, FOR SESSION 12h;

-- Very short tokens for high-security environments
DEFINE ACCESS high_sec ON DATABASE TYPE RECORD
    SIGNUP (...)
    SIGNIN (...)
    DURATION FOR TOKEN 5m, FOR SESSION 1h;

-- Longer durations for less sensitive applications
DEFINE ACCESS relaxed ON DATABASE TYPE RECORD
    SIGNUP (...)
    SIGNIN (...)
    DURATION FOR TOKEN 1h, FOR SESSION 7d;
```

---

## Row-Level Security (Table Permissions)

Permissions are defined on tables and control what record users can do. They are enforced automatically by the database engine -- there is no way for a record user to bypass them.

### Basic Permissions

```surrealql
DEFINE TABLE post SCHEMALESS
    PERMISSIONS
        FOR select WHERE published = true OR user = $auth.id
        FOR create WHERE $auth.id IS NOT NONE
        FOR update WHERE user = $auth.id
        FOR delete WHERE user = $auth.id OR $auth.role = 'admin';
```

### Granular Permission Examples

```surrealql
-- Public read, authenticated write
DEFINE TABLE article SCHEMALESS
    PERMISSIONS
        FOR select FULL       -- anyone can read (including unauthenticated)
        FOR create, update, delete WHERE $auth.id IS NOT NONE;

-- Owner-only access
DEFINE TABLE private_note SCHEMALESS
    PERMISSIONS
        FOR select, update, delete WHERE owner = $auth.id
        FOR create WHERE $auth.id IS NOT NONE;

-- No access for record users (admin-only table)
DEFINE TABLE system_config SCHEMALESS
    PERMISSIONS
        FOR select, create, update, delete NONE;

-- Role-based permissions
DEFINE TABLE order SCHEMAFULL
    PERMISSIONS
        FOR select WHERE
            customer = $auth.id
            OR $auth.role IN ['admin', 'support']
        FOR create WHERE $auth.id IS NOT NONE
        FOR update WHERE
            customer = $auth.id AND status = 'draft'
            OR $auth.role = 'admin'
        FOR delete WHERE $auth.role = 'admin';
```

### Multi-Tenant Permissions

```surrealql
-- Tenant isolation: users can only see data in their tenant
DEFINE TABLE customer SCHEMAFULL
    PERMISSIONS
        FOR select WHERE tenant = $auth.tenant
        FOR create WHERE tenant = $auth.tenant
        FOR update WHERE tenant = $auth.tenant AND $auth.role IN ['admin', 'editor']
        FOR delete WHERE tenant = $auth.tenant AND $auth.role = 'admin';

DEFINE TABLE invoice SCHEMAFULL
    PERMISSIONS
        FOR select WHERE
            tenant = $auth.tenant
            AND (
                created_by = $auth.id
                OR $auth.role IN ['admin', 'finance']
            )
        FOR create WHERE tenant = $auth.tenant
        FOR update WHERE
            tenant = $auth.tenant
            AND (created_by = $auth.id OR $auth.role = 'admin')
            AND status != 'finalized'
        FOR delete NONE;  -- invoices cannot be deleted
```

### Complex Permission Conditions

```surrealql
-- Time-based permissions
DEFINE TABLE submission SCHEMAFULL
    PERMISSIONS
        FOR select FULL
        FOR create WHERE
            $auth.id IS NOT NONE
            AND time::now() < d'2026-03-01T00:00:00Z'  -- submission deadline
        FOR update WHERE
            author = $auth.id
            AND status = 'draft'
            AND time::now() < d'2026-03-01T00:00:00Z'
        FOR delete WHERE author = $auth.id AND status = 'draft';

-- Permissions based on related records
DEFINE TABLE comment SCHEMAFULL
    PERMISSIONS
        FOR select WHERE
            -- Can see comments on posts you can see
            (SELECT VALUE published FROM ONLY post WHERE id = $parent.post) = true
            OR $auth.id IS NOT NONE
        FOR create WHERE $auth.id IS NOT NONE
        FOR update WHERE author = $auth.id
        FOR delete WHERE
            author = $auth.id
            OR $auth.role = 'moderator';

-- Access-method-specific permissions
DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select WHERE
            $access = 'account' AND id = $auth.id  -- record users see only themselves
            OR $access = 'admin_access'              -- admin access sees all
        FOR update WHERE id = $auth.id
        FOR delete NONE;
```

---

## Field-Level Permissions

### PERMISSIONS on DEFINE FIELD

```surrealql
-- Restrict field visibility and mutability
DEFINE TABLE user SCHEMAFULL
    PERMISSIONS FOR select, create, update WHERE $auth.id = id OR $auth.role = 'admin';

DEFINE FIELD email ON TABLE user TYPE string
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role = 'admin'
        FOR update WHERE id = $auth.id;

DEFINE FIELD pass ON TABLE user TYPE string
    PERMISSIONS
        FOR select NONE  -- password hash is never returned
        FOR update WHERE id = $auth.id;

DEFINE FIELD role ON TABLE user TYPE string
    PERMISSIONS
        FOR select FULL
        FOR update WHERE $auth.role = 'admin';  -- only admins can change roles

DEFINE FIELD salary ON TABLE user TYPE option<decimal>
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role IN ['admin', 'hr']
        FOR update WHERE $auth.role IN ['admin', 'hr'];

DEFINE FIELD internal_notes ON TABLE user TYPE option<string>
    PERMISSIONS
        FOR select WHERE $auth.role IN ['admin', 'hr']
        FOR update WHERE $auth.role = 'admin';
```

### Computed Field Security

```surrealql
-- Computed fields can enforce derived security values
DEFINE FIELD created_by ON TABLE document TYPE record<user>
    DEFAULT $auth.id
    READONLY;  -- cannot be overwritten after creation

DEFINE FIELD tenant ON TABLE document TYPE record<tenant>
    DEFAULT $auth.tenant
    READONLY;

-- Computed field that masks sensitive data based on viewer
DEFINE FIELD display_email ON TABLE user VALUE
    IF $auth.role = 'admin' OR $auth.id = id THEN
        email
    ELSE
        string::concat(
            string::slice(email, 0, 2),
            '***@',
            string::split(email, '@')[1]
        )
    END;
```

### Sensitive Data Masking

```surrealql
-- Credit card masking
DEFINE TABLE payment_method SCHEMAFULL;
DEFINE FIELD card_number ON TABLE payment_method TYPE string
    PERMISSIONS FOR select NONE;  -- raw number never returned
DEFINE FIELD masked_card ON TABLE payment_method VALUE
    string::concat('****-****-****-', string::slice(card_number, -4));
DEFINE FIELD cardholder ON TABLE payment_method TYPE string;
DEFINE FIELD expiry ON TABLE payment_method TYPE string;

-- SSN/sensitive ID masking
DEFINE FIELD ssn ON TABLE employee TYPE string
    PERMISSIONS
        FOR select WHERE $auth.role = 'hr_admin'
        FOR update WHERE $auth.role = 'hr_admin';
DEFINE FIELD masked_ssn ON TABLE employee VALUE
    string::concat('***-**-', string::slice(ssn, -4));
```

---

## Security Best Practices

### Principle of Least Privilege

```surrealql
-- Start with NONE and explicitly grant access
DEFINE TABLE sensitive_data SCHEMAFULL
    PERMISSIONS
        FOR select, create, update, delete NONE;

-- Then open up only what is needed
-- Better: grant specific access to specific roles
DEFINE TABLE project SCHEMAFULL
    PERMISSIONS
        FOR select WHERE
            team_member = $auth.id
            OR $auth.role IN ['admin', 'project_manager']
        FOR create WHERE $auth.role IN ['admin', 'project_manager']
        FOR update WHERE
            lead = $auth.id
            OR $auth.role = 'admin'
        FOR delete WHERE $auth.role = 'admin';
```

### Password Hashing

SurrealDB provides built-in cryptographic hashing functions. Always use argon2 for password storage.

```surrealql
-- Argon2 (recommended -- memory-hard, resistant to GPU attacks)
crypto::argon2::generate($password)
crypto::argon2::compare($hash, $password)

-- Bcrypt (acceptable alternative)
crypto::bcrypt::generate($password)
crypto::bcrypt::compare($hash, $password)

-- Scrypt (another memory-hard option)
crypto::scrypt::generate($password)
crypto::scrypt::compare($hash, $password)

-- SHA-256/512 (NOT suitable for passwords, use for data integrity only)
crypto::sha256($data)
crypto::sha512($data)

-- PBKDF2 (acceptable but argon2 is preferred)
crypto::pbkdf2::generate($password)
crypto::pbkdf2::compare($hash, $password)

-- NEVER store plaintext passwords
-- BAD:
CREATE user SET pass = $pass;
-- GOOD:
CREATE user SET pass = crypto::argon2::generate($pass);
```

### Token Duration Guidelines

| Use Case | Token Duration | Session Duration |
|---|---|---|
| Banking/financial | 5m | 30m |
| Enterprise SaaS | 15m | 8h |
| Consumer web app | 30m | 24h |
| Mobile app | 1h | 30d |
| Internal tool | 1h | 12h |
| IoT device | 24h | 90d |

```surrealql
-- High-security pattern: short tokens, moderate sessions
DEFINE ACCESS banking ON DATABASE TYPE RECORD
    SIGNUP (...)
    SIGNIN (...)
    DURATION FOR TOKEN 5m, FOR SESSION 30m;
```

### CORS Configuration

CORS is configured at the server level when starting SurrealDB, not in SurrealQL.

```bash
# Allow specific origins
surreal start --allow-origins "https://app.example.com,https://admin.example.com"

# Allow all origins (development only)
surreal start --allow-origins "*"

# Full server startup with security flags
surreal start \
    --bind 0.0.0.0:8000 \
    --user root \
    --pass "strong-root-password" \
    --allow-origins "https://app.example.com" \
    --strict \
    file:///var/data/surreal.db
```

### TLS/SSL Configuration

```bash
# Start with TLS
surreal start \
    --web-crt /etc/ssl/certs/server.crt \
    --web-key /etc/ssl/private/server.key \
    --bind 0.0.0.0:8000

# Client connections should use wss:// or https://
# wss://db.example.com:8000/rpc  (WebSocket with TLS)
# https://db.example.com:8000    (HTTP with TLS)
```

### Network Security for Distributed Deployments

```bash
# Bind only to private network interfaces
surreal start --bind 10.0.1.5:8000

# For TiKV distributed deployments, ensure:
# 1. TiKV nodes communicate over private network
# 2. PD (Placement Driver) is not exposed publicly
# 3. SurrealDB compute nodes connect to TiKV over private network
surreal start --kvs-ca /etc/tikv/ca.pem --kvs-crt /etc/tikv/client.crt --kvs-key /etc/tikv/client.key tikv://10.0.1.10:2379

# Use --strict mode in production to require authentication
surreal start --strict
```

### Audit Logging Patterns

```surrealql
-- Create an append-only audit log table
DEFINE TABLE audit_log SCHEMAFULL
    PERMISSIONS
        FOR select WHERE $auth.role = 'admin'
        FOR create FULL
        FOR update, delete NONE;  -- immutable records

DEFINE FIELD action ON TABLE audit_log TYPE string;
DEFINE FIELD table_name ON TABLE audit_log TYPE string;
DEFINE FIELD record_id ON TABLE audit_log TYPE option<record>;
DEFINE FIELD actor ON TABLE audit_log TYPE option<record<user>>;
DEFINE FIELD timestamp ON TABLE audit_log TYPE datetime DEFAULT time::now();
DEFINE FIELD details ON TABLE audit_log TYPE option<object>;

-- Attach audit events to sensitive tables
DEFINE EVENT audit_user_changes ON TABLE user WHEN $event IN ["CREATE", "UPDATE", "DELETE"] THEN {
    CREATE audit_log SET
        action = $event,
        table_name = 'user',
        record_id = $after.id ?? $before.id,
        actor = $auth.id,
        details = {
            before: IF $event != "CREATE" THEN $before ELSE NONE END,
            after: IF $event != "DELETE" THEN $after ELSE NONE END
        };
};

DEFINE EVENT audit_permission_changes ON TABLE system_config
    WHEN $event IN ["CREATE", "UPDATE", "DELETE"] THEN {
    CREATE audit_log SET
        action = $event,
        table_name = 'system_config',
        record_id = $after.id ?? $before.id,
        actor = $auth.id,
        details = { event: $event };
};
```

### Common Security Pitfalls

1. Using `PERMISSIONS FOR select FULL` on tables with sensitive data. This allows unauthenticated access.

2. Forgetting that `$auth` is NONE for unauthenticated requests. Always check `$auth.id IS NOT NONE` where authentication is required.

3. Not setting PERMISSIONS at all. By default, tables without PERMISSIONS allow full access to all authenticated system users (root, namespace, database) but deny access to record users.

4. Storing plaintext passwords. Always use `crypto::argon2::generate()`.

5. Using overly long token durations. Keep tokens short (5-30 minutes) and sessions reasonable.

6. Not using `--strict` mode in production. Without it, unauthenticated connections may have elevated access.

7. Exposing SurrealDB directly to the internet without TLS. Always use TLS in production.

8. Using HS256 JWT with a weak secret key. Use at least 256 bits of entropy or prefer asymmetric algorithms (RS256, ES256).

---

## Authentication Flows

### Signup/Signin Flow for Web Applications

```surrealql
-- 1. Define the access method
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP (
        CREATE user SET
            email = string::lowercase($email),
            pass = crypto::argon2::generate($pass),
            name = $name,
            created_at = time::now(),
            role = 'member'
    )
    SIGNIN (
        SELECT * FROM user
        WHERE email = string::lowercase($email)
        AND crypto::argon2::compare(pass, $pass)
    )
    DURATION FOR TOKEN 15m, FOR SESSION 12h;

-- 2. User table with permissions
DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role = 'admin'
        FOR update WHERE id = $auth.id
        FOR delete WHERE $auth.role = 'admin'
        FOR create NONE;  -- users are created only through SIGNUP

DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
DEFINE FIELD pass ON TABLE user TYPE string PERMISSIONS FOR select NONE;
DEFINE FIELD name ON TABLE user TYPE string;
DEFINE FIELD role ON TABLE user TYPE string DEFAULT 'member';
DEFINE FIELD created_at ON TABLE user TYPE datetime;
```

Client-side flow (using the JavaScript SDK):

```javascript
import Surreal from 'surrealdb';

const db = new Surreal();
await db.connect('wss://db.example.com/rpc');
await db.use({ namespace: 'production', database: 'app' });

// Sign up
const signupToken = await db.signup({
    access: 'account',
    variables: {
        email: 'user@example.com',
        pass: 'secure-password',
        name: 'Alice'
    }
});

// Sign in
const signinToken = await db.signin({
    access: 'account',
    variables: {
        email: 'user@example.com',
        pass: 'secure-password'
    }
});

// Authenticate with existing token
await db.authenticate(signinToken);

// All subsequent queries are scoped to this user
const myProfile = await db.select('user');
// Returns only the authenticated user's record (due to PERMISSIONS)
```

### JWT Token Integration with External Identity Providers

```surrealql
-- Define JWT access that maps external tokens to SurrealDB permissions
DEFINE ACCESS external_idp ON DATABASE TYPE RECORD
    WITH JWT ALGORITHM RS256 KEY '-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----'
    DURATION FOR TOKEN 1h;

-- The JWT payload should include claims that map to user data
-- Example JWT payload:
-- {
--   "sub": "auth0|12345",
--   "email": "user@example.com",
--   "roles": ["editor"],
--   "tenant_id": "tenant:acme",
--   "exp": 1700000000
-- }

-- Access JWT claims in permissions via $token
DEFINE TABLE document SCHEMAFULL
    PERMISSIONS
        FOR select WHERE tenant = $token.tenant_id
        FOR create WHERE 'editor' IN $token.roles
        FOR update WHERE 'editor' IN $token.roles AND tenant = $token.tenant_id
        FOR delete WHERE 'admin' IN $token.roles;
```

### Session Management

```surrealql
-- Define explicit session tracking
DEFINE TABLE session SCHEMAFULL
    PERMISSIONS
        FOR select WHERE user = $auth.id
        FOR create WHERE $auth.id IS NOT NONE
        FOR update, delete WHERE user = $auth.id;

DEFINE FIELD user ON TABLE session TYPE record<user>;
DEFINE FIELD device ON TABLE session TYPE string;
DEFINE FIELD ip_address ON TABLE session TYPE string;
DEFINE FIELD created_at ON TABLE session TYPE datetime DEFAULT time::now();
DEFINE FIELD last_active ON TABLE session TYPE datetime DEFAULT time::now();
DEFINE FIELD expires_at ON TABLE session TYPE datetime;

-- Create session on signin
DEFINE EVENT track_signin ON TABLE user WHEN $event = "UPDATE"
    AND $after.last_signin != $before.last_signin THEN {
    CREATE session SET
        user = $after.id,
        device = $after.current_device,
        ip_address = $after.current_ip,
        expires_at = time::now() + 12h;
};

-- Clean expired sessions (run periodically via application or cron)
DELETE session WHERE expires_at < time::now();
```

### Multi-Tenant Security with Namespaces

```surrealql
-- Strategy 1: One namespace per tenant (strongest isolation)
-- Each tenant gets their own namespace with identical schema

-- Tenant A
USE NS tenant_a DB main;
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP (CREATE user SET email = $email, pass = crypto::argon2::generate($pass))
    SIGNIN (SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass))
    DURATION FOR TOKEN 15m, FOR SESSION 12h;

-- Tenant B (completely isolated)
USE NS tenant_b DB main;
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP (CREATE user SET email = $email, pass = crypto::argon2::generate($pass))
    SIGNIN (SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass))
    DURATION FOR TOKEN 15m, FOR SESSION 12h;
```

```surrealql
-- Strategy 2: Shared database with tenant column (simpler, less isolation)
USE NS production DB shared;

DEFINE TABLE tenant SCHEMAFULL
    PERMISSIONS FOR select, create, update, delete NONE;  -- admin only

DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select WHERE tenant = $auth.tenant
        FOR update WHERE id = $auth.id
        FOR create, delete NONE;
DEFINE FIELD tenant ON TABLE user TYPE record<tenant> READONLY;

DEFINE TABLE data SCHEMAFULL
    PERMISSIONS
        FOR select WHERE tenant = $auth.tenant
        FOR create WHERE tenant = $auth.tenant
        FOR update WHERE tenant = $auth.tenant
        FOR delete WHERE tenant = $auth.tenant AND $auth.role = 'admin';
DEFINE FIELD tenant ON TABLE data TYPE record<tenant> DEFAULT $auth.tenant READONLY;

-- The READONLY + DEFAULT ensures the tenant field is automatically set
-- and cannot be tampered with by the user
```

---

## Security Checklist for Production

Before deploying SurrealDB to production:

- Use `--strict` mode to require authentication for all connections
- Enable TLS with valid certificates (`--web-crt`, `--web-key`)
- Set strong root passwords (minimum 20 characters, random)
- Define PERMISSIONS on every table that record users access
- Use `PERMISSIONS FOR select NONE` on password/secret fields
- Use `crypto::argon2::generate()` for all password storage
- Set appropriate token and session durations
- Restrict CORS to specific origins (not `*`)
- Bind to private network interfaces where possible
- Enable audit logging on sensitive tables
- Review all `FULL` permissions for unintended public access
- Ensure `$auth.id IS NOT NONE` checks where authentication is required
- Use SCHEMAFULL tables to prevent schema injection
- Set `READONLY` on fields that should not be user-modifiable (tenant, created_by)
- Use asymmetric JWT algorithms (RS256, ES256) over symmetric (HS256) when possible
- Regularly rotate JWT signing keys
- Test permissions thoroughly with different user roles
