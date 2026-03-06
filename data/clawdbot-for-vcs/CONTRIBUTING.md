# Contributing to Clawdbot for VCs

Thanks for your interest in improving this skill! This skill is designed to be community-driven and continuously improved based on real-world VC workflows.

---

## Philosophy

This skill follows these principles:

1. **Ship fast, iterate based on real usage** - Bias toward action over perfection
2. **Focus on investment partners** - Not broad firm management
3. **Safe by default** - Always ask before external actions
4. **Customizable but opinionated** - Strong defaults, easy to adapt

---

## Ways to Contribute

### 1. Share Feedback & Usage Patterns

The most valuable contribution is sharing what works and what doesn't:

- **What saves you time?** Which workflows are most valuable?
- **What's broken?** Edge cases, bugs, confusing documentation
- **What's missing?** Gaps in the workflow or documentation

**How to share:**
- Open a GitHub Issue with the `feedback` label
- Include your use case and specific examples
- No need to propose solutions — problems are valuable input

### 2. Report Bugs

Found something that doesn't work as expected?

**Good bug reports include:**
1. What you tried to do
2. What you expected to happen
3. What actually happened
4. Relevant logs or error messages (redact sensitive info)

**Open an issue** with the `bug` label.

### 3. Improve Documentation

Documentation is critical for adoption. Improvements welcome:

- **Clarify confusing sections** - If something tripped you up, it'll trip others up
- **Add examples** - Real-world examples are more valuable than abstract docs
- **Fix typos/errors** - Even small fixes help

**Submit a PR** with changes to markdown files.

### 4. Add Features

Want to add a new workflow or capability?

**Before coding:**
1. Open an issue with the `feature` label
2. Describe the use case and proposed approach
3. Get feedback from maintainers and other users

**When coding:**
- Keep it focused on investment partner workflows
- Maintain the "safe by default" philosophy (ask before external actions)
- Update documentation in the same PR
- Include example usage

### 5. Share Customizations

Built something cool for your specific workflow?

**Consider sharing:**
- Custom email templates that work well
- Affinity workflow variations
- Integration with other tools (Slack, Notion, etc.)
- Advanced automation patterns

**How to share:**
- Open a PR to add to `examples/` directory
- Or open an issue with description and code snippets
- Document requirements and setup steps

---

## Development Guidelines

### Code Style

This skill primarily consists of:
- **Markdown documentation** (SKILL.md, BOOTSTRAP.md, README.md)
- **Bash scripts** (for tool integration)
- **Template files** (AGENTS.md, USER.md, TOOLS.md examples)

**Guidelines:**
- Write clear, concise prose
- Use examples liberally
- Assume basic command line familiarity
- Test all code snippets before submitting

### Documentation Style

**Voice:**
- Direct and practical (not academic)
- Conversational but professional
- Actionable (tell people what to do, not just what exists)

**Structure:**
- Clear headings and sections
- Use tables for reference data
- Include code blocks with syntax highlighting
- Link between related sections

**Examples:**
- Real-world scenarios over abstract descriptions
- Show both the command and expected output
- Include common mistakes and how to fix them

### Testing Changes

**Before submitting:**
1. Test all bash commands in a clean environment
2. Verify all links work
3. Check that examples are accurate
4. Read through as if you're a new user

**No automated tests yet** - this is workflow documentation, so manual testing is primary.

---

## Pull Request Process

### 1. Fork & Branch

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/clawdbot-for-vcs.git
cd clawdbot-for-vcs

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Keep commits focused and atomic
- Write clear commit messages
- Update documentation if behavior changes

### 3. Test Locally

- Verify all examples work
- Check that new workflows integrate cleanly
- Test with fresh config (pretend you're a new user)

### 4. Submit PR

**PR title format:**
- `docs: clarify Affinity setup steps`
- `feat: add Notion CRM integration`
- `fix: correct Gmail label IDs in example`
- `chore: update dependencies`

**PR description should include:**
- What changed and why
- How to test the change
- Any breaking changes or migration steps
- Screenshots (if relevant)

**Example:**
```markdown
## Summary
Adds support for auto-generating call prep documents when meetings are scheduled.

## Changes
- New workflow in SKILL.md for call prep automation
- Updated AGENTS.md.example with call prep trigger
- Added example call prep template

## Testing
1. Schedule a meeting via booking link
2. AI should detect new event and offer to prep
3. Generated prep doc includes Affinity data + pitch deck

## Notes
- Requires calendar events to have company name in title
- Pitch deck must be in Gmail or Affinity
```

### 5. Code Review

Maintainers will review and may request changes. Common feedback:

- "Can you add an example of this?"
- "Let's clarify this section for new users"
- "How does this interact with [existing feature]?"

**Be responsive** - PRs with stale conversations get closed.

---

## Types of Contributions We're Looking For

### High Priority

✅ **Documentation improvements** - Clarity, examples, troubleshooting
✅ **Bug fixes** - Broken workflows, incorrect examples
✅ **Integration recipes** - How to connect with other tools (Slack, Notion, etc.)
✅ **Real-world examples** - "Here's how I use this in production"

### Medium Priority

🟡 **New workflows** - Additional VC-specific automation
🟡 **Template variations** - Alternative email templates, memo formats
🟡 **Tool support** - Alternative CRMs, email clients (if demand exists)

### Low Priority (for now)

🔴 **Non-VC use cases** - Keep focused on investment partner workflows
🔴 **Firm-wide management** - This is individual workflow automation
🔴 **Dramatic architecture changes** - Stability matters for production use

---

## Community Guidelines

**Be helpful and respectful:**
- Assume good intent
- Provide constructive feedback
- Share knowledge generously
- Help newcomers get started

**Be practical:**
- Focus on real-world usage
- Avoid over-engineering
- Ship iteratively, improve over time

**Be transparent:**
- Share what works AND what doesn't
- Document limitations honestly
- Credit others' contributions

---

## Questions?

Not sure if your contribution is a good fit? **Just ask!**

- Open an issue with your idea
- Tag it `question`
- We'll discuss and provide guidance

No contribution is too small. Documentation fixes, typo corrections, and usage feedback are all valuable.

---

## Release Process

Maintainers follow semantic versioning:

- **v1.x.x** - Current stable release
- **v1.x+1.x** - Minor features, backward compatible
- **v2.x.x** - Major changes, may require migration

**Changelog:**
- All changes documented in CHANGELOG.md
- Follow [Keep a Changelog](https://keepachangelog.com/) format

---

## Recognition

Contributors will be recognized in:
- CHANGELOG.md (for significant contributions)
- README.md (major feature additions)
- GitHub contributor list

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make VC workflows more efficient!** 🚀
