# Authentication & Authorization Patterns

Master authentication and authorization patterns including JWT, OAuth2, session management, and RBAC to build secure, scalable access control systems.

## Description

USE WHEN:
- Implementing user authentication systems
- Securing REST or GraphQL APIs
- Adding OAuth2/social login or SSO
- Designing session management
- Implementing RBAC or permission systems
- Debugging authentication issues

DON'T USE WHEN:
- Only need UI/login page styling
- Task is infrastructure-only without identity concerns
- Cannot change auth policies

---

## Authentication vs Authorization

| AuthN (Authentication) | AuthZ (Authorization) |
|------------------------|----------------------|
| "Who are you?" | "What can you do?" |
| Verify identity | Check permissions |
| Issue credentials | Enforce policies |
| Login/logout | Access control |

---

## Authentication Strategies

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Session** | Simple, secure | Stateful, scaling | Traditional web apps |
| **JWT** | Stateless, scalable | Token size, revocation | APIs, microservices |
| **OAuth2/OIDC** | Delegated, SSO | Complex setup | Social login, enterprise |

---

## JWT Implementation

### Generate Tokens

```typescript
import jwt from 'jsonwebtoken';

function generateTokens(user: User) {
  const accessToken = jwt.sign(
    { userId: user.id, email: user.email, role: user.role },
    process.env.JWT_SECRET!,
    { expiresIn: '15m' }  // Short-lived
  );

  const refreshToken = jwt.sign(
    { userId: user.id },
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: '7d' }  // Long-lived
  );

  return { accessToken, refreshToken };
}
```

### Verify Middleware

```typescript
function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.substring(7);
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!);
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Refresh Token Flow

```typescript
app.post('/api/auth/refresh', async (req, res) => {
  const { refreshToken } = req.body;
  
  try {
    // Verify refresh token
    const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET!);
    
    // Check if token exists in database (not revoked)
    const storedToken = await db.refreshTokens.findOne({
      token: await hash(refreshToken),
      expiresAt: { $gt: new Date() }
    });
    
    if (!storedToken) {
      return res.status(403).json({ error: 'Token revoked' });
    }
    
    // Generate new access token
    const user = await db.users.findById(payload.userId);
    const accessToken = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET!,
      { expiresIn: '15m' }
    );
    
    res.json({ accessToken });
  } catch {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});
```

---

## Session-Based Authentication

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',  // HTTPS only
    httpOnly: true,   // No JavaScript access
    maxAge: 24 * 60 * 60 * 1000,  // 24 hours
    sameSite: 'strict'  // CSRF protection
  }
}));

// Login
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await db.users.findOne({ email });
  
  if (!user || !(await verifyPassword(password, user.passwordHash))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  req.session.userId = user.id;
  req.session.role = user.role;
  res.json({ user: { id: user.id, email: user.email } });
});

// Logout
app.post('/api/auth/logout', (req, res) => {
  req.session.destroy(() => {
    res.clearCookie('connect.sid');
    res.json({ message: 'Logged out' });
  });
});
```

---

## OAuth2 / Social Login

```typescript
import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  callbackURL: '/api/auth/google/callback'
}, async (accessToken, refreshToken, profile, done) => {
  // Find or create user
  let user = await db.users.findOne({ googleId: profile.id });
  
  if (!user) {
    user = await db.users.create({
      googleId: profile.id,
      email: profile.emails?.[0]?.value,
      name: profile.displayName
    });
  }
  
  return done(null, user);
}));

// Routes
app.get('/api/auth/google', 
  passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get('/api/auth/google/callback',
  passport.authenticate('google', { session: false }),
  (req, res) => {
    const tokens = generateTokens(req.user);
    res.redirect(`${FRONTEND_URL}/auth/callback?token=${tokens.accessToken}`);
  });
```

---

## Authorization: RBAC

```typescript
enum Role {
  USER = 'user',
  MODERATOR = 'moderator',
  ADMIN = 'admin'
}

const roleHierarchy: Record<Role, Role[]> = {
  [Role.ADMIN]: [Role.ADMIN, Role.MODERATOR, Role.USER],
  [Role.MODERATOR]: [Role.MODERATOR, Role.USER],
  [Role.USER]: [Role.USER]
};

function hasRole(userRole: Role, requiredRole: Role): boolean {
  return roleHierarchy[userRole].includes(requiredRole);
}

function requireRole(...roles: Role[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    if (!roles.some(role => hasRole(req.user.role, role))) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

// Usage
app.delete('/api/users/:id',
  authenticate,
  requireRole(Role.ADMIN),
  async (req, res) => {
    await db.users.delete(req.params.id);
    res.json({ message: 'User deleted' });
  }
);
```

---

## Permission-Based Access

```typescript
enum Permission {
  READ_USERS = 'read:users',
  WRITE_USERS = 'write:users',
  DELETE_USERS = 'delete:users',
  READ_POSTS = 'read:posts',
  WRITE_POSTS = 'write:posts'
}

const rolePermissions: Record<Role, Permission[]> = {
  [Role.USER]: [Permission.READ_POSTS, Permission.WRITE_POSTS],
  [Role.MODERATOR]: [Permission.READ_POSTS, Permission.WRITE_POSTS, Permission.READ_USERS],
  [Role.ADMIN]: Object.values(Permission)
};

function requirePermission(...permissions: Permission[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) return res.status(401).json({ error: 'Not authenticated' });
    
    const hasAll = permissions.every(p => 
      rolePermissions[req.user.role]?.includes(p)
    );
    
    if (!hasAll) return res.status(403).json({ error: 'Insufficient permissions' });
    next();
  };
}
```

---

## Resource Ownership

```typescript
function requireOwnership(resourceType: 'post' | 'comment') {
  return async (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) return res.status(401).json({ error: 'Not authenticated' });
    
    // Admins can access anything
    if (req.user.role === Role.ADMIN) return next();
    
    const resource = await db[resourceType].findById(req.params.id);
    if (!resource) return res.status(404).json({ error: 'Not found' });
    
    if (resource.userId !== req.user.userId) {
      return res.status(403).json({ error: 'Not authorized' });
    }
    
    next();
  };
}

// Usage: Users can only update their own posts
app.put('/api/posts/:id', authenticate, requireOwnership('post'), updatePost);
```

---

## Password Security

```typescript
import bcrypt from 'bcrypt';
import { z } from 'zod';

const passwordSchema = z.string()
  .min(12, 'Password must be at least 12 characters')
  .regex(/[A-Z]/, 'Must contain uppercase')
  .regex(/[a-z]/, 'Must contain lowercase')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^A-Za-z0-9]/, 'Must contain special character');

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);  // 12 rounds
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

---

## Best Practices

### ✅ Do

- Use HTTPS everywhere
- Hash passwords with bcrypt (12+ rounds)
- Use short-lived access tokens (15-30 min)
- Store refresh tokens in database (revocable)
- Validate all input
- Rate limit auth endpoints
- Log security events
- Use secure cookie flags (httpOnly, secure, sameSite)

### ❌ Don't

- Store passwords in plain text
- Store JWT in localStorage (XSS vulnerable)
- Use weak JWT secrets
- Trust client-side auth checks only
- Expose stack traces in errors
- Skip server-side validation
- Ignore rate limiting

---

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| JWT in localStorage | Use httpOnly cookies |
| No token expiration | Set short TTL + refresh tokens |
| Weak passwords | Enforce strong policy with zod |
| No rate limiting | Use express-rate-limit + Redis |
| Client-only auth | Always validate server-side |
