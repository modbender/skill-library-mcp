# Contributing to ClawMeter

Thank you for considering contributing to ClawMeter! This document outlines how to contribute effectively.

---

## 🤝 Ways to Contribute

1. **Report bugs** — Found a problem? Open an issue
2. **Request features** — Have an idea? Share it
3. **Update model pricing** — Providers change prices frequently
4. **Improve documentation** — Clarify setup or usage
5. **Enhance UI/UX** — Make the dashboard better
6. **Write tests** — Help us maintain quality
7. **Fix bugs** — Submit a PR for open issues

---

## 🐛 Reporting Bugs

Before opening an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Reproduce the bug** in a clean environment
3. **Collect logs** from the terminal and browser console

**Good bug report includes:**
- **Description:** What went wrong?
- **Steps to reproduce:** How can we trigger it?
- **Expected behavior:** What should happen?
- **Actual behavior:** What actually happened?
- **Environment:** OS, Node version, OpenClaw version
- **Logs/screenshots:** Any relevant error messages

**Template:**
```markdown
## Bug Description
ClawMeter dashboard shows $0.00 even after running ingest.

## Steps to Reproduce
1. Install ClawMeter
2. Run `npm run ingest`
3. Run `npm start`
4. Open http://localhost:3377

## Expected Behavior
Dashboard should show actual spending data.

## Actual Behavior
All stats show $0.00.

## Environment
- OS: Ubuntu 22.04
- Node: v20.10.0
- OpenClaw: v1.5.2

## Logs
```
✅ Ingested 0 new usage events
```

## Troubleshooting Attempted
- Verified OPENCLAW_AGENTS_DIR path
- Checked that .jsonl files exist
- No errors in browser console
```

---

## 💡 Requesting Features

**Good feature requests include:**
- **Use case:** Why do you need this?
- **Current workaround:** How do you solve it now?
- **Proposed solution:** How should it work?
- **Alternatives considered:** Other approaches you've thought about

**Template:**
```markdown
## Feature Request

### Problem
I want to track costs per project, but ClawMeter only shows per-session data.

### Use Case
I work on multiple client projects and need to allocate costs accurately.

### Proposed Solution
Add a "project" tag to sessions (via label or metadata) and show cost breakdown by project in the dashboard.

### Alternatives Considered
- Manually exporting data and processing in Excel
- Running separate ClawMeter instances per project

### Additional Context
This would help teams doing client billing or internal cost allocation.
```

---

## 🔧 Development Setup

### Prerequisites

- Node.js v18+
- Git
- OpenClaw installed (for testing)

### Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/clawmeter.git
   cd clawmeter
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenClaw agents path
   ```

5. **Run initial ingest:**
   ```bash
   npm run ingest
   ```

6. **Start development server:**
   ```bash
   npm run dev
   ```

7. **Open dashboard:**
   http://localhost:3377

---

## 🎨 Code Style

### JavaScript

- **ES modules** (`import`/`export`, not `require`)
- **Modern syntax** (async/await, destructuring, arrow functions)
- **Consistent formatting:**
  - 2 spaces for indentation
  - Single quotes for strings
  - Semicolons required
  - Trailing commas in multiline objects/arrays

**Example:**
```javascript
export async function fetchData(url) {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to fetch:', error);
    return null;
  }
}
```

### HTML/CSS

- **Semantic HTML** (use appropriate tags)
- **CSS custom properties** for theming
- **Mobile-first responsive design**
- **Consistent naming:** BEM-inspired class names

### Comments

- **Why, not what:** Explain the reasoning, not the obvious
- **TODOs:** Mark future work with `// TODO: description`
- **Warnings:** Highlight edge cases with `// NOTE: ...`

---

## 📝 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `style:` — Formatting, whitespace (no code change)
- `refactor:` — Code restructuring (no feature change)
- `perf:` — Performance improvement
- `test:` — Adding or fixing tests
- `chore:` — Maintenance (deps, build, etc.)

**Examples:**
```bash
feat(api): add /api/export endpoint for CSV export

fix(ingest): handle corrupted .jsonl lines gracefully

docs(readme): add troubleshooting section for $0.00 dashboard

style(ui): improve mobile responsiveness for stat cards

refactor(pricing): extract model matching to separate function

chore(deps): update Chart.js to v4.5.0
```

---

## 🔀 Pull Request Process

### Before Submitting

1. **Test your changes** locally
2. **Update documentation** if behavior changes
3. **Add/update CHANGELOG.md** entry
4. **Ensure code follows style guide**
5. **Check for console errors** in browser and terminal

### Submitting

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub:
   - Clear title (follows commit message format)
   - Description of what changed and why
   - Link to related issues (if any)
   - Screenshots (for UI changes)

### PR Template

```markdown
## Description
Brief summary of what this PR does.

## Motivation
Why is this change needed?

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
How to test this PR:
1. Step 1
2. Step 2
3. Expected result

## Screenshots (if applicable)
[Attach before/after images for UI changes]

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Tested locally
- [ ] No console errors
```

---

## 🧪 Testing

### Manual Testing

Before submitting a PR, test:

1. **Ingest:** Run `npm run ingest` — should complete without errors
2. **Server:** Run `npm start` — should start on port 3377
3. **Dashboard:** Open http://localhost:3377 — should load correctly
4. **API:** Test endpoints manually (curl or browser)
5. **Auto-watch:** Generate new logs, verify auto-ingestion

### Test Checklist

- [ ] Fresh install works (delete `node_modules`, reinstall)
- [ ] Dashboard loads without JavaScript errors
- [ ] All API endpoints return valid JSON
- [ ] Charts render correctly
- [ ] Tables populate with data
- [ ] Budget calculations are accurate
- [ ] File watcher detects new logs
- [ ] Alerts trigger correctly (if configured)

---

## 📚 Documentation

### When to Update Docs

- **README.md:** For user-facing changes (features, setup, configuration)
- **SKILL.md:** For OpenClaw integration changes (commands, API, examples)
- **CHANGELOG.md:** For all notable changes
- **Code comments:** For complex logic or edge cases

### Writing Good Docs

- **Be concise:** Get to the point quickly
- **Use examples:** Show, don't just tell
- **Stay updated:** Docs drift is confusing
- **Think like a beginner:** Don't assume prior knowledge

---

## 🎯 Focus Areas

### High Priority

1. **Model pricing updates** — Providers change prices frequently
2. **Bug fixes** — Stability is critical
3. **Documentation improvements** — Clarity helps everyone

### Medium Priority

4. **UI/UX enhancements** — Make it more intuitive
5. **Performance optimizations** — Faster is better
6. **New features** — Expand functionality

### Low Priority

7. **Refactoring** — Don't break working code without reason
8. **Cosmetic changes** — Nice to have, but not essential

---

## 💬 Communication

### Where to Discuss

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and ideas
- **OpenClaw Discord:** Community chat and support

### Response Times

- **Issues:** We'll respond within 48 hours
- **PRs:** Review within 1 week
- **Urgent bugs:** Prioritized for faster turnaround

---

## 🏆 Recognition

Contributors will be:
- **Credited in CHANGELOG.md**
- **Listed in README.md** (for significant contributions)
- **Thanked publicly** on GitHub and Discord

---

## 📜 Code of Conduct

### Be Respectful

- **Assume good intent**
- **Be patient with beginners**
- **Critique code, not people**
- **Stay professional**

### Zero Tolerance

- **Harassment or discrimination**
- **Spam or self-promotion**
- **Trolling or inflammatory comments**

Violations will result in removal from the project.

---

## 🛠️ Specific Contribution Guides

### Adding Model Pricing

1. Open `src/pricing.mjs`
2. Add entry to `MODEL_PRICING` object:
   ```javascript
   'new-model-id': {
     input: 1.50,      // USD per million input tokens
     output: 6.00,     // USD per million output tokens
     cacheRead: 0.15,  // (optional) cache read discount
     cacheWrite: 1.88, // (optional) cache write pricing
   }
   ```
3. Test with example session containing that model
4. Update CHANGELOG.md
5. Submit PR with pricing source link

### Improving the Dashboard UI

1. Edit `web/index.html` (all UI code is in one file)
2. Test changes locally (hard refresh: Ctrl+Shift+R)
3. Ensure mobile responsiveness (test in DevTools)
4. Check dark mode compatibility
5. Verify Chart.js interactions still work
6. Take before/after screenshots
7. Submit PR with screenshots

### Adding API Endpoints

1. Add route in `src/server.mjs`:
   ```javascript
   app.get('/api/your-endpoint', (req, res) => {
     // Query database
     const result = db.prepare('SELECT ...').all();
     res.json(result);
   });
   ```
2. Update SKILL.md with endpoint documentation
3. Add example usage in README.md
4. Test manually: `curl http://localhost:3377/api/your-endpoint`
5. Submit PR

---

## 🙏 Thank You

Every contribution, no matter how small, helps make ClawMeter better for everyone.

**Questions?** Open a discussion on GitHub or ask in the OpenClaw Discord.

**Happy contributing! ⚡**
