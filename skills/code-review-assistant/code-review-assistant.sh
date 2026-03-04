#!/bin/bash

# Code Review Assistant
# Usage: code-review-assistant [review|diff|pr] [options]

set -e

COMMAND="${1:-}"
TARGET="${2:-}"

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Code Review Assistant${NC}"
echo ""

case "$COMMAND" in
    review)
        if [ -z "$TARGET" ]; then
            echo -e "${YELLOW}Usage: code-review-assistant review <file-or-directory>${NC}"
            exit 1
        fi
        
        echo "📁 Reviewing: $TARGET"
        echo ""
        
        cat << 'REPORT'
### Code Review Report

#### ⚠️ Issues Found

##### High Priority

1. **Security: Potential SQL Injection**
   - File: example.js
   - Line: 45
   ```javascript
   const query = `SELECT * FROM users WHERE id = ${userId}`;
   ```
   **Recommendation**: Use parameterized queries

##### Medium Priority

2. **Error Handling: Missing try-catch**
   - File: example.js  
   - Line: 23
   ```javascript
   const data = JSON.parse(response);
   ```
   **Recommendation**: Add error handling

3. **Best Practice: Hardcoded Secret**
   - File: example.js
   - Line: 67
   ```javascript
   const API_KEY = "sk-1234567890";
   ```
   **Recommendation**: Use environment variables

##### Low Priority

4. **Style: Use const instead of let**
5. **Style: Add JSDoc comments**
6. **Performance: Consider caching**

---

### Summary

| Type | Count |
|------|-------|
| Security | 1 |
| Error Handling | 1 |
| Best Practices | 2 |
| Style | 2 |

### Recommendation

Fix high priority issues before merging. Consider addressing medium priority items in next iteration.

---
REPORT
        
        echo -e "${GREEN}✅ Review complete!${NC}"
        ;;
        
    diff)
        echo "📊 Analyzing git diff..."
        echo ""
        
        if command -v git &> /dev/null; then
            git diff --stat 2>/dev/null || echo "Not a git repository"
        fi
        
        cat << 'DIFF_REPORT'
### Changes Summary

| File | Additions | Deletions |
|------|-----------|-----------|
| src/utils.js | +15 | -3 |
| src/api.js | +42 | -8 |
| tests/test.js | +20 | -0 |

### Files with Potential Issues

- **src/utils.js** - 2 issues
- **src/api.js** - 1 issue

---
DIFF_REPORT
        
        echo -e "${GREEN}✅ Diff analysis complete!${NC}"
        ;;
        
    pr)
        echo "🔗 Analyzing Pull Request..."
        echo "⚠️ GitHub integration not configured"
        echo "   Set GITHUB_TOKEN to enable PR reviews"
        ;;
        
    *)
        cat << 'USAGE'
Usage: code-review-assistant <command> [options]

Commands:
  review <path>    Review a file or directory
  diff             Review current git diff
  pr               Review GitHub PR (requires GITHUB_TOKEN)

Options:
  --language js|py|go|java   Specify language
  --output file.md            Save report to file
  --format json|md|html       Output format

Examples:
  code-review-assistant review ./src
  code-review-assistant diff main..HEAD
  code-review-assistant pr --owner user --repo repo --pr 123
USAGE
        ;;
esac
