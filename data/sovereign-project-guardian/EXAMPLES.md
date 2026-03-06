# Sovereign Project Guardian -- Examples

## Example: Taking a Node.js Project from F to A

This example walks through a real-world scenario where a project starts with a failing grade and is improved step by step to reach an A.

---

## Initial State -- Grade F (Score: 18/100)

### Project Structure (Before)

```
my-api/
  src/
    index.js
    routes/
      users.js
      products.js
    db.js
  node_modules/
  package.json
```

### Initial Audit Report

```
## Project Health Report

**Project:** my-api
**Type:** Node.js Web Application
**Date:** 2026-02-23
**Guardian:** sovereign-project-guardian v1.0.0

### Overall Grade: F (18/100)

### Category Breakdown

| Category | Score | Checks Passed | Checks Failed |
|----------|-------|---------------|---------------|
| Security (30%) | 0/100 | 0 | 4 |
| Quality (25%) | 0/100 | 0 | 4 |
| Documentation (20%) | 0/100 | 0 | 3 |
| CI/CD & Ops (15%) | 0/100 | 0 | 3 |
| Code Hygiene (10%) | 33/100 | 1 | 2 |

### Detailed Findings

#### Security
- [FAIL] S1: Secrets found in source code
  - `src/db.js:3` contains database password: "dbpass123"
  - `src/routes/users.js:1` contains JWT secret: "mysecret"
- [FAIL] S2: No .gitignore -- .env files would be committed
- [FAIL] S3: package.json uses wildcard versions ("express": "*")
  - No package-lock.json found
- [FAIL] S4: No security middleware (no helmet, no CORS config, no rate limiting)

#### Quality
- [FAIL] Q1: No tests found (no test directory, no test files, no test script)
- [FAIL] Q2: No coverage configuration
- [FAIL] Q3: No linting configured (no .eslintrc, no prettier config)
- [FAIL] Q4: No TypeScript or type checking

#### Documentation
- [FAIL] D1: No README.md
- [FAIL] D2: No LICENSE file
- [FAIL] D3: No CHANGELOG.md

#### CI/CD & Operations
- [FAIL] O1: No CI/CD pipeline (.github/workflows/ not found)
- [FAIL] O2: No code review process artifacts
- [WARN] O3: No Dockerfile

#### Code Hygiene
- [FAIL] H1: No .gitignore file
- [PASS] H2: No large binary files
- [FAIL] H3: No code formatting configuration
```

---

## Step 1: Fix Critical Security Issues -- Grade D (Score: 42/100)

### Actions Taken

**1a. Remove hardcoded secrets and use environment variables:**

```javascript
// src/db.js -- BEFORE
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: 'postgres://admin:dbpass123@localhost:5432/myapp'
});
module.exports = pool;
```

```javascript
// src/db.js -- AFTER
const { Pool } = require('pg');

if (!process.env.DATABASE_URL) {
  console.error('FATAL: DATABASE_URL environment variable is required');
  process.exit(1);
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: true } : false
});

module.exports = pool;
```

**1b. Create .gitignore:**

```
# .gitignore
node_modules/
dist/
.env
.env.*
!.env.example
*.log
coverage/
```

**1c. Create .env.example:**

```
DATABASE_URL=postgres://user:password@localhost:5432/myapp
JWT_SECRET=change-me-to-a-random-64-char-string
NODE_ENV=development
PORT=3000
```

**1d. Pin dependency versions and generate lock file:**

```bash
# Replace wildcard versions with exact versions
npm install --save-exact express pg jsonwebtoken
# This creates package-lock.json with pinned versions
```

**Result after Step 1:**
- S1: PASS (secrets removed)
- S2: PASS (.env in .gitignore)
- S3: PASS (pinned versions + lock file)
- S4: Still FAIL
- Grade: D (42/100) -- security cap removed, but still many gaps

---

## Step 2: Add Security Middleware and Tests -- Grade C (Score: 63/100)

### Actions Taken

**2a. Add security middleware:**

```bash
npm install --save-exact helmet cors express-rate-limit
```

```javascript
// src/index.js -- add security middleware
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per window
  standardHeaders: true,
  legacyHeaders: false
}));
```

**2b. Add tests:**

```bash
npm install --save-dev --save-exact jest supertest
mkdir tests
```

```javascript
// tests/users.test.js
const request = require('supertest');
const app = require('../src/index');

describe('GET /api/users', () => {
  it('returns 200 with a list of users', async () => {
    const res = await request(app).get('/api/users');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('returns 400 for invalid query parameters', async () => {
    const res = await request(app).get('/api/users?page=-1');
    expect(res.status).toBe(400);
  });
});
```

```json
// package.json -- add test script
{
  "scripts": {
    "test": "jest --coverage",
    "start": "node src/index.js"
  }
}
```

**2c. Add ESLint and Prettier:**

```bash
npm install --save-dev --save-exact eslint prettier eslint-config-prettier
```

```json
// .eslintrc.json
{
  "env": { "node": true, "es2021": true, "jest": true },
  "extends": ["eslint:recommended", "prettier"],
  "rules": {
    "no-unused-vars": "error",
    "no-console": ["warn", { "allow": ["error"] }],
    "eqeqeq": "error"
  }
}
```

**Result after Step 2:**
- S4: PASS (helmet + cors + rate limiting)
- Q1: PASS (tests exist)
- Q3: PASS (ESLint + Prettier configured)
- Grade: C (63/100) -- no more caps, solid foundation

---

## Step 3: Add Documentation and CI -- Grade B (Score: 82/100)

### Actions Taken

**3a. Create README.md:**

```markdown
# My API

REST API for user and product management.

## Installation

    npm install

## Configuration

Copy `.env.example` to `.env` and fill in values:

    cp .env.example .env

## Usage

    npm start

## Testing

    npm test

## Contributing

See CONTRIBUTING.md for guidelines. All PRs require at least one review.

## License

MIT
```

**3b. Create LICENSE (MIT)**

**3c. Create CHANGELOG.md:**

```markdown
# Changelog

## [1.1.0] - 2026-02-23

### Added
- Security middleware (helmet, CORS, rate limiting)
- Test suite with Jest
- ESLint and Prettier configuration
- Environment variable configuration

### Security
- Removed hardcoded credentials from source code
- Added .gitignore with secret file patterns
- Pinned all dependency versions
```

**3d. Create GitHub Actions CI:**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
```

**Result after Step 3:**
- D1: PASS, D2: PASS, D3: PASS
- O1: PASS
- Grade: B (82/100)

---

## Step 4: Polish to A -- Grade A (Score: 94/100)

### Final Actions

**4a. Add coverage thresholds:**

```javascript
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 }
  }
};
```

**4b. Add TypeScript (or JSDoc types):**

```bash
npm install --save-dev --save-exact typescript @types/node @types/express
npx tsc --init --strict
```

**4c. Add pre-commit hooks:**

```bash
npm install --save-dev --save-exact husky lint-staged
npx husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.{js,ts}": ["eslint --fix", "prettier --write"]
  }
}
```

**4d. Add Dockerfile:**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY src/ ./src/
USER app
EXPOSE 3000
CMD ["node", "src/index.js"]
```

**4e. Add PR template and CODEOWNERS:**

```markdown
<!-- .github/pull_request_template.md -->
## What
Brief description of changes.

## Why
Why this change is needed.

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing done

## Checklist
- [ ] No secrets in code
- [ ] Lint passes
- [ ] Tests pass
```

### Final Report

```
## Project Health Report

**Project:** my-api
**Overall Grade: A (94/100)

| Category | Score |
|----------|-------|
| Security (30%) | 100/100 |
| Quality (25%) | 100/100 |
| Documentation (20%) | 88/100 |
| CI/CD & Ops (15%) | 83/100 |
| Code Hygiene (10%) | 100/100 |

All critical and high-priority items resolved.
```

### Final Project Structure

```
my-api/
  .github/
    workflows/ci.yml
    pull_request_template.md
  src/
    index.js
    routes/users.js
    routes/products.js
    db.js
  tests/
    users.test.js
    products.test.js
  .editorconfig
  .env.example
  .eslintrc.json
  .gitignore
  .prettierrc
  CHANGELOG.md
  CODEOWNERS
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.md
  jest.config.js
  package.json
  package-lock.json
```

---

## License

MIT
