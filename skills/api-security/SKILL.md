---
name: API Security Best Practices
description: Implement secure API design patterns including authentication,
  authorization, input validation, rate limiting, and protection against common
  API vulnerabilities.
---

# API Security Best Practices

Implement secure API design patterns including authentication, authorization, input validation, rate limiting, and protection against common API vulnerabilities.

## Description

USE WHEN:
- Designing new API endpoints
- Securing existing APIs
- Implementing authentication and authorization (JWT, OAuth 2.0, API keys)
- Setting up rate limiting and throttling
- Protecting against injection attacks (SQL, XSS, command)
- Conducting API security reviews or preparing for audits
- Handling sensitive data in APIs
- Building REST, GraphQL, or WebSocket APIs

DON'T USE WHEN:
- Need vulnerability scanning (use `vulnerability-scanner` skill)
- Building frontend-only apps with no API
- Need network-level security (firewalls, WAF config)

OUTPUTS:
- Secure authentication implementations (JWT, refresh tokens)
- Input validation schemas (Zod, Joi)
- Rate limiting configurations
- Security middleware examples
- OWASP API Top 10 compliance guidance

---

## How It Works

### Step 1: Authentication & Authorization

- Choose authentication method (JWT, OAuth 2.0, API keys)
- Implement token-based authentication
- Set up role-based access control (RBAC)
- Secure session management
- Implement multi-factor authentication (MFA)

### Step 2: Input Validation & Sanitization

- Validate all input data
- Sanitize user inputs
- Use parameterized queries
- Implement request schema validation
- Prevent SQL injection, XSS, and command injection

### Step 3: Rate Limiting & Throttling

- Implement rate limiting per user/IP
- Set up API throttling
- Configure request quotas
- Handle rate limit errors gracefully
- Monitor for suspicious activity

### Step 4: Data Protection

- Encrypt data in transit (HTTPS/TLS)
- Encrypt sensitive data at rest
- Implement proper error handling (no data leaks)
- Sanitize error messages
- Use secure headers

---

## JWT Authentication Implementation

### Generate Secure JWT Tokens

```javascript
// auth.js
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Validate input
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }
    
    // Find user
    const user = await db.user.findUnique({ where: { email } });
    
    if (!user) {
      // Don't reveal if user exists
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Verify password
    const validPassword = await bcrypt.compare(password, user.passwordHash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '1h', issuer: 'your-app', audience: 'your-app-users' }
    );
    
    // Generate refresh token
    const refreshToken = jwt.sign(
      { userId: user.id },
      process.env.JWT_REFRESH_SECRET,
      { expiresIn: '7d' }
    );
    
    // Store refresh token in database
    await db.refreshToken.create({
      data: {
        token: refreshToken,
        userId: user.id,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      }
    });
    
    res.json({ token, refreshToken, expiresIn: 3600 });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'An error occurred during login' });
  }
});
```

### JWT Verification Middleware

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }
  
  jwt.verify(
    token, 
    process.env.JWT_SECRET,
    { issuer: 'your-app', audience: 'your-app-users' },
    (err, user) => {
      if (err) {
        if (err.name === 'TokenExpiredError') {
          return res.status(401).json({ error: 'Token expired' });
        }
        return res.status(403).json({ error: 'Invalid token' });
      }
      req.user = user;
      next();
    }
  );
}

module.exports = { authenticateToken };
```

---

## Input Validation (SQL Injection Prevention)

### ❌ Vulnerable Code

```javascript
// NEVER DO THIS - SQL Injection vulnerability
app.get('/api/users/:id', async (req, res) => {
  const userId = req.params.id;
  const query = `SELECT * FROM users WHERE id = '${userId}'`;
  const user = await db.query(query);
  res.json(user);
});

// Attack: GET /api/users/1' OR '1'='1 → Returns all users!
```

### ✅ Safe: Parameterized Queries

```javascript
app.get('/api/users/:id', async (req, res) => {
  const userId = req.params.id;
  
  // Validate input first
  if (!userId || !/^\d+$/.test(userId)) {
    return res.status(400).json({ error: 'Invalid user ID' });
  }
  
  // Use parameterized query
  const user = await db.query(
    'SELECT id, email, name FROM users WHERE id = $1',
    [userId]
  );
  
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  
  res.json(user);
});
```

### ✅ Safe: Using ORM (Prisma)

```javascript
app.get('/api/users/:id', async (req, res) => {
  const userId = parseInt(req.params.id);
  
  if (isNaN(userId)) {
    return res.status(400).json({ error: 'Invalid user ID' });
  }
  
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { id: true, email: true, name: true } // Don't select sensitive fields
  });
  
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  
  res.json(user);
});
```

### Schema Validation with Zod

```javascript
const { z } = require('zod');

const createUserSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[a-z]/, 'Must contain lowercase letter')
    .regex(/[0-9]/, 'Must contain number'),
  name: z.string().min(2).max(100),
  age: z.number().int().min(18).max(120).optional()
});

function validateRequest(schema) {
  return (req, res, next) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      res.status(400).json({ error: 'Validation failed', details: error.errors });
    }
  };
}

app.post('/api/users', validateRequest(createUserSchema), async (req, res) => {
  // Input is validated at this point
  const { email, password, name, age } = req.body;
  const passwordHash = await bcrypt.hash(password, 10);
  const user = await prisma.user.create({ data: { email, passwordHash, name, age } });
  const { passwordHash: _, ...userWithoutPassword } = user;
  res.status(201).json(userWithoutPassword);
});
```

---

## Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const Redis = require('ioredis');

const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT
});

// General API rate limit
const apiLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:api:' }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: { error: 'Too many requests, please try again later', retryAfter: 900 },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.user?.userId || req.ip
});

// Strict rate limit for authentication
const authLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:auth:' }),
  windowMs: 15 * 60 * 1000,
  max: 5, // Only 5 login attempts per 15 minutes
  skipSuccessfulRequests: true,
  message: { error: 'Too many login attempts, please try again later', retryAfter: 900 }
});

app.use('/api/', apiLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
```

---

## Security Headers (Helmet)

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:']
    }
  },
  frameguard: { action: 'deny' },
  hidePoweredBy: true,
  noSniff: true,
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true }
}));
```

---

## Authorization Checks

### ❌ Bad: Only Authentication

```javascript
app.delete('/api/posts/:id', authenticateToken, async (req, res) => {
  await prisma.post.delete({ where: { id: req.params.id } });
  res.json({ success: true });
});
```

### ✅ Good: Authentication + Authorization

```javascript
app.delete('/api/posts/:id', authenticateToken, async (req, res) => {
  const post = await prisma.post.findUnique({ where: { id: req.params.id } });
  
  if (!post) {
    return res.status(404).json({ error: 'Post not found' });
  }
  
  // Check if user owns the post or is admin
  if (post.userId !== req.user.userId && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Not authorized to delete this post' });
  }
  
  await prisma.post.delete({ where: { id: req.params.id } });
  res.json({ success: true });
});
```

---

## Best Practices

### ✅ Do This

- **Use HTTPS Everywhere** - Never send sensitive data over HTTP
- **Implement Authentication** - Require authentication for protected endpoints
- **Validate All Inputs** - Never trust user input
- **Use Parameterized Queries** - Prevent SQL injection
- **Implement Rate Limiting** - Protect against brute force and DDoS
- **Hash Passwords** - Use bcrypt with salt rounds >= 10
- **Use Short-Lived Tokens** - JWT access tokens should expire quickly
- **Implement CORS Properly** - Only allow trusted origins
- **Log Security Events** - Monitor for suspicious activity
- **Use Security Headers** - Implement Helmet.js
- **Sanitize Error Messages** - Don't leak sensitive information

### ❌ Don't Do This

- **Don't Store Passwords in Plain Text**
- **Don't Use Weak Secrets** - Use strong, random JWT secrets
- **Don't Trust User Input** - Always validate and sanitize
- **Don't Expose Stack Traces** - Hide error details in production
- **Don't Use String Concatenation for SQL**
- **Don't Store Sensitive Data in JWT** - JWTs are not encrypted
- **Don't Ignore Security Updates** - Update dependencies regularly
- **Don't Log Sensitive Data**

---

## OWASP API Security Top 10

1. **Broken Object Level Authorization** - Always verify user can access resource
2. **Broken Authentication** - Implement strong authentication mechanisms
3. **Broken Object Property Level Authorization** - Validate which properties user can access
4. **Unrestricted Resource Consumption** - Implement rate limiting and quotas
5. **Broken Function Level Authorization** - Verify user role for each function
6. **Unrestricted Access to Sensitive Business Flows** - Protect critical workflows
7. **Server Side Request Forgery (SSRF)** - Validate and sanitize URLs
8. **Security Misconfiguration** - Use security best practices and headers
9. **Improper Inventory Management** - Document and secure all API endpoints
10. **Unsafe Consumption of APIs** - Validate data from third-party APIs

---

## Security Checklist

### Authentication & Authorization
- [ ] Implement strong authentication (JWT, OAuth 2.0)
- [ ] Use HTTPS for all endpoints
- [ ] Hash passwords with bcrypt (salt rounds >= 10)
- [ ] Implement token expiration
- [ ] Add refresh token mechanism
- [ ] Verify user authorization for each request
- [ ] Implement role-based access control (RBAC)

### Input Validation
- [ ] Validate all user inputs
- [ ] Use parameterized queries or ORM
- [ ] Sanitize HTML content
- [ ] Validate file uploads
- [ ] Implement request schema validation
- [ ] Use allowlists, not blocklists

### Rate Limiting & DDoS Protection
- [ ] Implement rate limiting per user/IP
- [ ] Add stricter limits for auth endpoints
- [ ] Use Redis for distributed rate limiting
- [ ] Return proper rate limit headers
- [ ] Implement request throttling

### Data Protection
- [ ] Use HTTPS/TLS for all traffic
- [ ] Encrypt sensitive data at rest
- [ ] Don't store sensitive data in JWT
- [ ] Sanitize error messages
- [ ] Implement proper CORS configuration
- [ ] Use security headers (Helmet.js)

---

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)
- [API Security Checklist](https://github.com/shieldfy/API-Security-Checklist)
