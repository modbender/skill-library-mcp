# Contributing

PRs welcome. Please:

1. Keep the three-layer architecture intact (bootstrap hook / message hook / plugin tool block)
2. No external runtime dependencies beyond `openclaw/plugin-sdk`
3. Hook handlers must have zero runtime imports — Node 24 type stripping only, no `import` statements that execute at runtime
4. Test against a real OpenClaw instance before submitting
5. Update CHANGELOG.md with any user-facing changes
