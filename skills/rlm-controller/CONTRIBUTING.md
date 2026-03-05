# Contributing to RLM Controller

Thank you for your interest in contributing to RLM Controller! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** and clone it locally
2. **Review the security model** in [docs/security.md](docs/security.md)
3. **Test your changes** with sample inputs
4. **Document your changes** in relevant docs

## Security First

RLM Controller is designed for safe operation with untrusted inputs. All contributions must:

- ✅ Never execute arbitrary model-generated code
- ✅ Maintain strict bounds on resource usage
- ✅ Treat all input as potentially malicious
- ✅ Use only safelisted operations
- ✅ Follow principle of least privilege

See [docs/security_checklist.md](docs/security_checklist.md) for operational guidelines.

## Code Style

- **Python**: Follow PEP 8 style guide
- **Scripts**: Include docstrings with usage examples
- **Comments**: Explain *why*, not *what*
- **Error handling**: Fail gracefully with clear messages

## Testing

Before submitting:

```bash
# Smoke test core utilities
python3 scripts/rlm_ctx.py --help
python3 scripts/rlm_plan.py --help
python3 scripts/rlm_auto.py --help

# Test with sample input
echo "test content" > /tmp/test.txt
python3 scripts/rlm_ctx.py store --infile /tmp/test.txt --ctx-dir /tmp/ctx
```

## Documentation

Update documentation when:
- Adding new scripts or features
- Changing command-line interfaces
- Modifying security policies or limits
- Adding new workflows

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with clear commit messages
3. **Update documentation** as needed
4. **Test thoroughly** - both happy path and error cases
5. **Submit PR** with description of changes and rationale

### PR Checklist

- [ ] Code follows project style
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Scripts tested with sample inputs
- [ ] No breaking changes to existing workflows
- [ ] Commit messages are clear

## Reporting Issues

When reporting bugs or issues:

1. **Check existing issues** first
2. **Provide context**: OS, Python version, OpenClaw version
3. **Include reproduction steps** if possible
4. **Redact sensitive data** from logs/traces

## Feature Requests

We welcome feature requests! Please:

- Explain the **use case** and motivation
- Consider **security implications**
- Propose how it fits with existing architecture
- Be open to alternative approaches

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

## Questions?

- Review existing documentation in `docs/`
- Check closed issues for similar questions
- Open a discussion issue for clarification

Thank you for helping make RLM Controller better!
