# Bundle Manifest

The published skill bundle should include these repo-root paths:

- `SKILL.md`
- `README.md`
- `LICENSE`
- `agents/openai.yaml`
- `scripts/massive`
- `references/massive-api.md`
- `references/openclaw-secrets.md`
- `references/security.md`
- `tests/test_massive.sh`

If a distributed artifact omits `scripts/massive`, treat it as a packaging error and regenerate the bundle from the repository root.
