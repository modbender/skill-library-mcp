#!/usr/bin/env bash
set -euo pipefail

cd "$1"

git init
git config user.email "dev@taskflow.local"
git config user.name "TaskFlow Developer"

# =============================================================================
# Initial commit: feat: initial project setup
# =============================================================================
mkdir -p src

cat > package.json << 'JSONEOF'
{
  "name": "taskflow-api",
  "version": "1.2.3",
  "description": "TaskFlow API Server",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "echo \"tests pass\""
  }
}
JSONEOF

cat > src/version.js << 'JSEOF'
module.exports = {
  VERSION: "1.2.3",
  BUILD_DATE: "2025-01-15"
};
JSEOF

cat > src/index.js << 'JSEOF'
const { VERSION } = require('./version');
console.log(`TaskFlow API v${VERSION} starting...`);
JSEOF

cat > src/api.js << 'JSEOF'
const express = require('express');
// TODO(v1.3): Add rate limiting middleware
// Current endpoints handle basic CRUD for tasks

function setupRoutes(app) {
  app.get('/tasks', (req, res) => res.json([]));
  app.post('/tasks', (req, res) => res.status(201).json(req.body));
}

module.exports = { setupRoutes };
JSEOF

cat > src/auth.js << 'JSEOF'
// TODO(v1.3): Implement token refresh endpoint
// Currently only supports initial token generation

function generateToken(user) {
  return { token: 'mock-token', expires: '1h' };
}

function validateToken(token) {
  return token === 'mock-token';
}

module.exports = { generateToken, validateToken };
JSEOF

cat > README.md << 'MDEOF'
# TaskFlow API

![Version](https://img.shields.io/badge/version-1.2.3-blue)

A task management API server.

## Quick Start
```
npm start
```

## API Version
Current version: 1.2.3
MDEOF

cat > CHANGELOG.md << 'MDEOF'
# Changelog

## [1.2.3] - 2025-01-15
### Fixed
- Resolved race condition in concurrent task updates

## [1.2.2] - 2025-01-02
### Fixed
- Fixed date parsing for non-UTC timezones

## [1.2.1] - 2024-12-20
### Fixed
- Corrected pagination cursor encoding

## [1.2.0] - 2024-12-10
### Added
- Webhook notifications for task status changes
- Batch delete endpoint

## [1.1.0] - 2024-11-15
### Added
- Task assignment and delegation
- Email notifications

## [1.0.0] - 2024-10-01
### Added
- Initial release
- Basic task CRUD operations
- User authentication
MDEOF

cat > release-checklist.md << 'MDEOF'
# Release Checklist

Follow these steps in order when preparing a release:

1. [ ] Verify all TODO items for this version are resolved
   - Search for `TODO(vX.Y)` comments matching the target version
   - Either implement or remove with explanation

2. [ ] Update version number in ALL locations:
   - `package.json` → `version` field
   - `src/version.js` → `VERSION` constant
   - `src/version.js` → `BUILD_DATE` to today's date
   - `README.md` → version badge and "Current version" text

3. [ ] Update CHANGELOG.md:
   - Add new section at top: `## [X.Y.Z] - YYYY-MM-DD`
   - List all changes since previous version under appropriate categories:
     - `### Added` for new features
     - `### Fixed` for bug fixes
     - `### Changed` for modifications to existing features
   - Check git log for commits since last version tag

4. [ ] Create release commit:
   - Stage all changes
   - Commit with message: `release: vX.Y.Z`

5. [ ] Create version tag:
   - `git tag vX.Y.Z`
MDEOF

git add -A
git commit -m "feat: initial project setup"

# Create v1.2.3 tag
git tag v1.2.3

# =============================================================================
# Commit 2: feat: add user preference API endpoint
# =============================================================================
cat > src/preferences.js << 'JSEOF'
// User preference management
// Allows users to set notification, theme, and language preferences

function getPreferences(userId) {
  return {
    userId,
    theme: 'light',
    notifications: true,
    language: 'en'
  };
}

function updatePreferences(userId, prefs) {
  return { ...getPreferences(userId), ...prefs };
}

module.exports = { getPreferences, updatePreferences };
JSEOF

git add -A
git commit -m "feat: add user preference API endpoint"

# =============================================================================
# Commit 3: feat: add bulk export capability
# =============================================================================
cat > src/export.js << 'JSEOF'
// Bulk export functionality
// Supports exporting tasks in JSON and CSV formats

function exportTasks(tasks, format) {
  if (format === 'csv') {
    const header = 'id,title,status,assignee\n';
    const rows = tasks.map(t => `${t.id},${t.title},${t.status},${t.assignee}`);
    return header + rows.join('\n');
  }
  return JSON.stringify(tasks, null, 2);
}

function exportToFile(tasks, format, filepath) {
  const data = exportTasks(tasks, format);
  // In production, would write to filepath
  return { success: true, path: filepath, size: data.length };
}

module.exports = { exportTasks, exportToFile };
JSEOF

git add -A
git commit -m "feat: add bulk export capability"

# =============================================================================
# Commit 4: fix: correct pagination offset calculation
# =============================================================================
cat > src/api.js << 'JSEOF'
const express = require('express');
// TODO(v1.3): Add rate limiting middleware
// Current endpoints handle basic CRUD for tasks

function setupRoutes(app) {
  app.get('/tasks', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;
    res.json({ data: [], offset, limit, page });
  });
  app.post('/tasks', (req, res) => res.status(201).json(req.body));
}

module.exports = { setupRoutes };
JSEOF

git add -A
git commit -m "fix: correct pagination offset calculation"

# =============================================================================
# Commit 5: chore: update dev dependencies
# =============================================================================
cat > package.json << 'JSONEOF'
{
  "name": "taskflow-api",
  "version": "1.2.3",
  "description": "TaskFlow API Server",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "echo \"tests pass\""
  },
  "devDependencies": {
    "eslint": "^8.50.0",
    "prettier": "^3.0.0",
    "jest": "^29.7.0"
  }
}
JSONEOF

git add -A
git commit -m "chore: update dev dependencies"
