# Contributing to ClawTV

Thanks for your interest in making ClawTV better! We welcome contributions of all kinds — bug fixes, new features, documentation improvements, and ideas.

## How to Contribute

1. **Fork the repo** — Click the "Fork" button on GitHub
2. **Clone your fork** — `git clone https://github.com/YOUR-USERNAME/clawtv.git`
3. **Create a branch** — `git checkout -b fix-screenshot-bug` (use a descriptive name)
4. **Make your changes** — Write code, fix bugs, update docs
5. **Test locally** — Make sure it works on your Apple TV setup
6. **Commit with sign-off** — `git commit -s -m "Fix screenshot timing issue"` (see DCO below)
7. **Push to your fork** — `git push origin fix-screenshot-bug`
8. **Open a Pull Request** — Go to the original repo and click "New Pull Request"

We'll review your PR and provide feedback. Don't worry if it's not perfect — we're happy to help refine it!

## Code Style

ClawTV is intentionally minimal — the entire project is a single Python file. Here's what we care about:

- **Keep it simple** — Avoid adding heavy dependencies unless absolutely necessary
- **Follow existing patterns** — Match the style of the surrounding code (4-space indents, descriptive variable names)
- **Comment complex logic** — If it's not obvious, explain why (not just what)
- **Docstrings for functions** — Brief description of what it does and any key parameters

**Example:**
```python
async def send_remote_command(atv, command):
    """Send a single remote control command to the Apple TV.
    
    Args:
        atv: Connected pyatv device instance
        command: String like 'up', 'down', 'select', 'menu'
    """
    # implementation...
```

## Developer Certificate of Origin (DCO)

By contributing to ClawTV, you certify that:

1. The contribution was created in whole or in part by you and you have the right to submit it under the MIT license.
2. You understand and agree that the contribution is public and that a record of it (including your sign-off) is maintained permanently.

This is the same [DCO](https://developercertificate.org/) used by the Linux kernel and many other projects.

**How to sign off:** Add the `-s` flag when committing:
```bash
git commit -s -m "Add support for volume control"
```

This appends a `Signed-off-by: Your Name <your.email@example.com>` line to your commit message, certifying you have the right to submit the code under the MIT license.

**All commits must be signed off.** If you forget, you can amend your last commit:
```bash
git commit --amend -s --no-edit
git push --force-with-lease
```

## Ideas for Contributions

Not sure where to start? Check the [README's Contributing section](README.md#contributing) for ideas:

- Alternative screenshot methods (eliminate Xcode dependency)
- Linux/Windows support
- Web UI with live screenshot feed
- Multi-TV support
- Voice control mode
- Screenshot caching / diff detection

Or browse the [Issues](https://github.com/akivasolutions/clawtv/issues) for bugs and feature requests.

## Questions?

Open an issue or start a discussion — we're happy to help!
