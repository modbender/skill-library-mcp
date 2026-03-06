# Contributing to Security Skill Scanner

Thank you for your interest in making the OpenClaw ecosystem safer! 🛡️

## How You Can Help

### 1. Report Malicious Skills

Found a malicious skill that our scanner doesn't detect?

**Submit an issue with:**
- Skill name and source (ClawHub URL or GitHub repo)
- What malicious behavior it exhibits
- Example code snippet showing the issue
- Suggested detection pattern

**Report here:** https://github.com/anikrahman0/security-skill-scanner/issues

### 2. Add Detection Patterns

Help us detect new types of malicious code!

**Steps:**
1. Fork the repository
2. Add your pattern to `SECURITY_PATTERNS` in `scanner.js`
3. Add test cases
4. Submit a pull request

**Example:**

```javascript
NEW_MALWARE_PATTERN: {
  level: 'CRITICAL',  // CRITICAL, HIGH, MEDIUM, LOW
  patterns: [
    /your-regex-pattern-here/gi,
    /another-pattern/gi,
  ],
  description: 'Brief description of what this detects',
  recommendation: 'What users should do if this is found'
}
```

### 3. Improve Documentation

- Fix typos or unclear explanations
- Add more examples
- Translate to other languages
- Create video tutorials

### 4. Test and Report Bugs

- Test with different skill types
- Report false positives
- Suggest improvements to detection logic
- Test on different operating systems

### 5. Share Knowledge

- Write blog posts about security
- Share the scanner with others
- Educate about skill security
- Contribute to discussions

## Development Guidelines

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/security-skill-scanner.git
cd security-skill-scanner

# Create a branch
git checkout -b feature/my-new-pattern

# Make your changes
# ...

# Test your changes
node test.js

# Commit and push
git add .
git commit -m "Add detection for XYZ malware pattern"
git push origin feature/my-new-pattern
```

### Code Style

- Use clear, descriptive variable names
- Add comments for complex logic
- Follow existing code formatting
- Keep functions focused and small
- Include error handling

### Adding a New Pattern

1. **Research the threat** - Understand what you're detecting
2. **Create regex pattern(s)** - Test thoroughly
3. **Choose appropriate risk level**:
   - CRITICAL: Immediate threat (code execution, data theft)
   - HIGH: Serious concern (sensitive file access, suspicious APIs)
   - MEDIUM: Potential issue (broad permissions, quality concerns)
   - LOW: Minor problem (code quality, documentation)

4. **Write clear descriptions** - Help users understand the risk
5. **Provide actionable recommendations** - Tell users what to do

### Testing Your Changes

Create test cases:

```bash
# Create a test file
mkdir -p test/my-pattern

# On Windows
md test\my-pattern

# Create test skill
# Add your test code to test/my-pattern/SKILL.md

# Run the scanner
node scanner.js test/my-pattern/SKILL.md

# Verify it detects your pattern
```

### Submitting a Pull Request

**PR Checklist:**
- [ ] Code follows project style
- [ ] Tests pass (`node test.js`)
- [ ] New patterns are documented
- [ ] Examples added if needed
- [ ] README updated if necessary
- [ ] Commit messages are clear

**PR Template:**

```markdown
## Description
Brief description of what this PR adds/fixes

## Type of Change
- [ ] New detection pattern
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Motivation
Why is this change needed?

## Testing
How did you test this change?

## Screenshots/Examples
If applicable, show before/after
```

## Pattern Contribution Examples

### Example 1: Detecting Cryptocurrency Mining

```javascript
CRYPTO_MINING: {
  level: 'CRITICAL',
  patterns: [
    /coinhive/gi,
    /cryptonight/gi,
    /monero.*?miner/gi,
    /stratum\+tcp/gi,
  ],
  description: 'Cryptocurrency mining code detected',
  recommendation: 'DO NOT INSTALL - This skill may use your CPU for mining cryptocurrency'
}
```

### Example 2: Detecting Data Exfiltration

```javascript
DATA_EXFILTRATION: {
  level: 'HIGH',
  patterns: [
    /navigator\.sendBeacon/gi,
    /\.addEventListener.*?beforeunload.*?fetch/gi,
  ],
  description: 'Potential data exfiltration on page unload',
  recommendation: 'Review what data is being sent when leaving the page'
}
```

### Example 3: Detecting Keyloggers

```javascript
KEYLOGGER: {
  level: 'CRITICAL',
  patterns: [
    /addEventListener.*?['"]keypress['"]/gi,
    /addEventListener.*?['"]keydown['"]/gi,
    /onkeypress.*?fetch|axios|XMLHttpRequest/gi,
  ],
  description: 'Possible keylogger - captures keyboard input',
  recommendation: 'DO NOT INSTALL - This may record your keystrokes'
}
```

## False Positive Handling

When adding patterns, consider false positives:

### Good Pattern (Specific)
```javascript
// Detects actual malicious eval usage
/eval\s*\(\s*['"]/gi  // eval with string argument
```

### Poor Pattern (Too Broad)
```javascript
// Too broad - catches legitimate "evaluation" text
/eval/gi
```

### Using Negative Lookahead
```javascript
// Exclude legitimate uses
/exec\s*\((?!['"]npm install)/gi
```

## Whitelist Management

When patterns might flag legitimate code:

```javascript
// In isWhitelisted() method
const legitimateUses = [
  'npm install',
  'pip install',
  'github.com',
  'githubusercontent.com'
];
```

## Documentation Standards

### Pattern Documentation

Each pattern should include:
- **Clear name** - What it detects
- **Risk level** - How serious it is
- **Description** - What behavior is flagged
- **Recommendation** - What users should do
- **Examples** - Real-world cases it catches

### Code Comments

```javascript
// GOOD: Explains WHY, not just WHAT
// Check for base64 encoding which may hide malicious payloads
// Common in obfuscation attempts by malware authors
const base64Pattern = /[A-Za-z0-9+\/]{40,}={0,2}/;

// BAD: States the obvious
// Regex for base64
const base64Pattern = /[A-Za-z0-9+\/]{40,}={0,2}/;
```

## Community Standards

### Be Respectful
- Assume good intentions
- Provide constructive feedback
- Help others learn
- Celebrate contributions

### Security First
- Verify patterns thoroughly
- Don't add untested code
- Consider edge cases
- Think like an attacker

### Quality Over Quantity
- One good pattern > many poor ones
- Test before submitting
- Document thoroughly
- Keep code maintainable

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in the community
- Helping make OpenClaw safer for everyone!

## Questions?

- **Technical Questions**: https://github.com/anikrahman0/security-skill-scanner/discussions
- **Bug Reports**: https://github.com/anikrahman0/security-skill-scanner/issues
- **Security Vulnerabilities**: Use GitHub Security tab to report privately
- **Direct Contact**: a7604366@gmail.com (for urgent security matters)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping keep the OpenClaw community safe!** 🙏
