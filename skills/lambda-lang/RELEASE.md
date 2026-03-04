# Lambda Lang Release Process

Follow this checklist when releasing a new version of Lambda Lang:

## 1. Update Code

- [ ] `src/atoms.json` — Update version and changelog
- [ ] `src/lambda_lang.py` — Python translator
- [ ] `src/go/lambda.go` — Go translator
- [ ] `src/roundtrip_test.py` — Add/update tests

## 2. Run Tests

```bash
cd src && python3 roundtrip_test.py
```

Ensure all tests pass.

## 3. Update Documentation

- [ ] `SKILL.md` — Update version number and changelog
- [ ] `README.md` — Update status, changelog, and relevant sections

## 4. Git Commit & Push

```bash
git add -A
git commit -m "release: vX.Y.Z - Description"
git push origin main
```

## 5. Publish to ClawHub

```bash
clawhub publish /path/to/lambda-lang --version X.Y.Z --changelog "Description"
```

## 6. Create GitHub Release

```bash
# Via API or GitHub UI
# Tag: vX.Y.Z
# Title: vX.Y.Z - Short description
# Body: Detailed changelog
```

## Checklist

| Step | Done |
|------|------|
| atoms.json version updated | ☐ |
| Python translator updated | ☐ |
| Go translator updated | ☐ |
| Tests passing | ☐ |
| SKILL.md updated | ☐ |
| README.md updated | ☐ |
| Git commit pushed | ☐ |
| ClawHub published | ☐ |
| GitHub Release created | ☐ |

---

*Last updated: v1.8.0 (2026-02-17)*
