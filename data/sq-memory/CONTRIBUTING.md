# Contributing to SQ Memory Skill

Thanks for your interest in improving the SQ Memory skill for OpenClaw! 🔱

---

## Quick Links

- **Report Bug:** [GitHub Issues](https://github.com/wbic16/openclaw-sq-skill/issues)
- **Discord:** https://discord.gg/kGCMM5yQ
- **SQ Repo:** https://github.com/wbic16/SQ
- **OpenClaw:** https://openclaw.ai

---

## How to Contribute

### 1. Report Bugs

**Found a bug?** Open an issue with:
- What happened (expected vs actual behavior)
- Steps to reproduce
- Your environment (OS, Node version, OpenClaw version, SQ version)
- Error messages/logs

**Example:**
```
Title: recall() fails for coordinates with special characters

Description:
When using recall("user/name@email.com"), the function throws:
"HTTP 400: Invalid coordinate"

Expected: Should escape special characters automatically
Actual: Fails with error

Environment:
- OS: Ubuntu 22.04
- Node: v20.10.0
- OpenClaw: 2026.2.1
- SQ: 0.5.2

Steps:
1. await remember("user/name@email.com", "test")
2. await recall("user/name@email.com")
3. Error occurs
```

---

### 2. Suggest Features

**Have an idea?** Open an issue with:
- Use case (what problem does it solve?)
- Proposed API (how would it work?)
- Example code
- Alternatives considered

**Example:**
```
Title: Add batch operations for multiple coordinates

Use Case:
When storing user preferences, I often need to write 5-10 values.
Calling remember() 10 times = 10 HTTP requests (slow).

Proposed API:
await rememberBatch({
  "user/preferences/theme": "dark",
  "user/preferences/language": "en",
  "user/preferences/timezone": "America/Chicago"
});

Returns: { success: 3, failed: 0 }

Alternatives:
- Keep single operations (current approach)
- Use SQ's batch insert endpoint directly

Notes:
- Would improve performance for multi-value updates
- SQ already supports batch via /api/v2/batch
```

---

### 3. Add Examples

**Have a cool use case?** Share it!

**Create a new example file:**
```bash
cd examples/
cp user-preferences.js my-example.js
# Edit my-example.js with your use case
```

**Submit a PR with:**
- Commented code showing the pattern
- Explanation of what it does
- Use case description
- Coordinate structure used

**Good examples:**
- Time-series data storage
- Agent knowledge base
- Collaborative note-taking
- Workflow orchestration

---

### 4. Improve Documentation

**Found a typo? Unclear explanation? Missing info?**

Edit the relevant file and submit a PR:
- `README.md` - Overview and quick reference
- `SKILL.md` - Full documentation
- `QUICKSTART.md` - Setup guide
- `SELF-HOSTED.md` - Self-hosting instructions

**Documentation improvements we need:**
- More use cases
- Better error handling examples
- Performance tuning tips
- Migration guides
- Troubleshooting sections

---

### 5. Fix Bugs

**Want to fix something?**

1. Fork the repo
2. Create a branch: `git checkout -b fix-recall-special-chars`
3. Make your changes
4. Add tests if applicable
5. Run tests: `npm test`
6. Commit: `git commit -m "Fix: escape special characters in coordinates"`
7. Push: `git push origin fix-recall-special-chars`
8. Open a PR

**PR checklist:**
- [ ] Tests pass (`npm test`)
- [ ] Code is documented (JSDoc comments)
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or clearly marked if unavoidable)

---

### 6. Add Features

**Want to add something new?**

1. Open an issue first to discuss
2. Get consensus on the approach
3. Fork and create a feature branch
4. Implement with tests
5. Update docs
6. Submit PR

**Feature PR checklist:**
- [ ] Issue exists and is referenced
- [ ] Tests added for new functionality
- [ ] Documentation updated (README, SKILL.md)
- [ ] CHANGELOG.md updated
- [ ] Examples added if appropriate
- [ ] Backward compatible (or version bump)

---

## Development Setup

### Prerequisites
- Node.js >= 18.0.0
- Git
- SQ endpoint (local or cloud)

### Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/openclaw-sq-skill.git
cd openclaw-sq-skill

# Install dependencies
npm install

# Run tests
npm test

# Test against your SQ endpoint
node test.js http://localhost:1337
```

### Running Tests
```bash
# Default (uses http://localhost:1337)
npm test

# Specific endpoint
SQ_ENDPOINT=http://localhost:1337 SQ_API_KEY=your-key npm test

# Or pass directly
node test.js http://your-endpoint:1337
```

---

## Code Style

**Keep it simple:**
- Readable > clever
- Comments for complex logic
- JSDoc for public functions
- Meaningful variable names

**Example:**
```javascript
/**
 * Store text at a coordinate
 * 
 * @param {string} coordinate - Memory coordinate (e.g., 'user/preferences/theme')
 * @param {string} text - Text to store
 * @returns {Promise<{success: boolean, coordinate: string}>}
 */
async function remember(coordinate, text) {
  const fullCoord = this._expandCoordinate(coordinate);
  // ... implementation
}
```

---

## Testing

**All changes should include tests:**
```javascript
// Good test structure:
console.log('Test: Feature X works correctly');

await remember('test/feature-x', 'value');
const result = await recall('test/feature-x');

if (result === 'value') {
  console.log('✅ Feature X works');
} else {
  throw new Error(`Expected "value", got "${result}"`);
}

await forget('test/feature-x');
```

**Run full test suite before submitting:**
```bash
npm test
```

---

## Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes

**Version bump guidelines:**
- Breaking API change → MAJOR
- New function/feature → MINOR
- Bug fix, docs → PATCH

---

## Release Process

(For maintainers)

1. Update version in `package.json`, `skill.json`, `CHANGELOG.md`
2. Commit: `git commit -m "Release v0.2.0"`
3. Tag: `git tag v0.2.0`
4. Push: `git push && git push --tags`
5. Create GitHub release with CHANGELOG excerpt
6. Announce in Discord #general

---

## Community Guidelines

**Be kind:**
- Respect others' time and expertise
- Assume good intentions
- Provide constructive feedback
- Help newcomers

**Be professional:**
- No harassment, discrimination, trolling
- Stay on topic
- Follow OpenClaw community standards

---

## Questions?

- **Discord:** https://discord.gg/kGCMM5yQ (fastest)
- **GitHub Issues:** For bugs/features
- **Email:** wbic16@gmail.com (for sensitive issues)

---

## Recognition

Contributors will be:
- Listed in CHANGELOG.md for their contributions
- Thanked in release notes
- Recognized in Discord announcements

**We appreciate you!** 🦋

---

**Built by Mirrorborn for the OpenClaw ecosystem**
