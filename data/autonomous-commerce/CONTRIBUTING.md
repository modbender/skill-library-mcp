# Contributing to Autonomous Commerce

Thank you for your interest in improving the autonomous commerce skill!

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or request features
- Include: OS, Node version, error messages, steps to reproduce
- For security issues, email directly (do not post publicly)

### Suggesting Enhancements
- Check existing issues first (avoid duplicates)
- Describe the use case and why it's valuable
- Provide examples if possible

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly** (we have real money at stake)
5. **Commit with clear messages:** `git commit -m "Add: feature description"`
6. **Push to your fork:** `git push origin feature/your-feature-name`
7. **Open a Pull Request**

### Development Guidelines

**Testing:**
- NEVER test with real payment methods on main branch
- Use test accounts or mock data for development
- Production testing requires explicit approval

**Security:**
- Never commit credentials (.env, auth.json, wallet.json)
- Use .gitignore properly
- Assume all code will be public

**Code Style:**
- ES modules (not CommonJS)
- Async/await (not callbacks)
- Clear variable names
- Comments for complex logic

**Documentation:**
- Update SKILL.md for behavior changes
- Update README.md for setup changes
- Update CHANGELOG.md for all changes
- Add JSDoc comments to functions

### Priority Areas for Contribution

**High Priority:**
1. **Multi-retailer support** (eBay, Walmart, Target)
2. **Better error handling** (payment declined, out of stock)
3. **Price tracking** (buy when price drops below threshold)
4. **Inventory monitoring** (buy when item back in stock)

**Medium Priority:**
5. **International shipping** support
6. **Gift purchases** (separate delivery address)
7. **Subscribe & Save** automation
8. **Return/refund** handling

**Nice to Have:**
9. Cross-retailer price comparison
10. Bulk purchase coordination
11. Warranty tracking

### What We're Looking For

- **Real-world usage feedback** (what worked, what didn't)
- **Edge case handling** (scenarios we haven't thought of)
- **Security improvements** (better guardrails)
- **Performance optimizations** (faster execution)
- **Documentation improvements** (clearer examples)

### What We're NOT Looking For

- Removing security guardrails (e.g., allowing new payment methods)
- Bypassing budget caps
- Credential harvesting or data exfiltration
- Spammy or scammy use cases

## Code of Conduct

**Be respectful.** This is a tool for automation, not abuse.

**Be responsible.** Test thoroughly. Don't break things.

**Be transparent.** If you discover a security issue, disclose it responsibly.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- **Moltbook:** https://moltbook.com/u/VHAGAR
- **GitHub Issues:** (when repo is public)
- **Email:** pandeaby@gmail.com (for sensitive matters)

---

**Thank you for helping build the future of autonomous commerce!**

*— VHAGAR/RAX*
