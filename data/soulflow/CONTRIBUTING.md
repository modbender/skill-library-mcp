# Contributing to SoulFlow

Thank you for your interest in contributing to SoulFlow! This document provides guidelines for contributing workflows, bug fixes, and features.

## Ways to Contribute

### 1. Share Workflows

The best way to contribute is by sharing your custom workflows. We're building a library of workflows for different domains:

- **Content creation** (research, writing, editing, publishing)
- **DevOps** (CI/CD, deployments, monitoring, incident response)
- **Research** (data gathering, analysis, synthesis, reporting)
- **Operations** (task automation, scheduling, notifications)
- **Testing** (test generation, execution, reporting)

**To share a workflow:**

1. Create your `.workflow.json` file (see README for format)
2. Test it thoroughly with `node soulflow.js run <workflow> "<task>"`
3. Submit a PR to add it to the `workflows/` directory
4. Include a description of what it does and example use cases

### 2. Report Bugs

Found a bug? Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Your OpenClaw and Node.js versions
- Relevant logs from `~/.openclaw/workspace/.soulflow/runs/<run-id>/`

### 3. Suggest Features

Have an idea? Open an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Why it would be useful to others

### 4. Code Contributions

**Before submitting a PR:**
- Discuss major changes in an issue first
- Keep changes focused (one feature/fix per PR)
- Test your changes with real workflows
- Update documentation if needed

**Code style:**
- Follow existing patterns
- Use clear variable names
- Add comments for complex logic
- Keep functions small and focused

## Development Setup

```bash
# Clone the repo
git clone https://github.com/soulstack/soulflow.git
cd soulflow

# Test connection
node soulflow.js test

# Run a workflow
node soulflow.js run security-audit "Test task"

# Check run history
node soulflow.js runs
```

## Workflow Design Best Practices

**Good workflows:**
- Have clear, descriptive step names
- Use explicit tool instructions ("Use `read` to...")
- Include "Do NOT just describe — actually do it" in prompts
- End with consistent status markers ("STATUS: done")
- Extract key variables with `KEY: value` format
- Keep steps focused on one task each

**Avoid:**
- Vague instructions ("figure out how to...")
- Skipping tool usage (describing instead of doing)
- Steps that depend on manual intervention
- Overly broad steps that do too much

## Testing Workflows

Before submitting:
1. Run the workflow end-to-end at least 3 times
2. Test with different task descriptions
3. Verify each step produces the expected output
4. Check that variables are correctly extracted and passed
5. Ensure timeouts are reasonable (default: 10 minutes per step)

## Documentation

When adding workflows:
- Add a section to README.md with example usage
- Document any special requirements (tools, APIs, etc.)
- Include sample output or screenshots if helpful

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue or reach out to [@TommyThomas0x](https://twitter.com/TommyThomas0x).
