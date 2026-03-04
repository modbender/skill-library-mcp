# ClawHub Publish Checklist (ACP-connected skill)

## Content checks

- [ ] `SKILL.md` explains ACP commerce path clearly
- [ ] No secrets committed (`token`, `key`, `.env`)
- [ ] Scripts point to preflight/setup_runner/publish flow
- [ ] `references/setup.md` updated with real env names

## Validation checks

- [ ] `scripts/smoke_test.sh` passes
- [ ] `scripts/preflight.sh` returns RUNNER_NOT_READY contract on clean machine
- [ ] proof/setup-url issue works on production control-plane

## Publish

```bash
clawhub login
clawhub publish ./skills/naver-blog-writer \
  --slug naver-blog-writer \
  --name "Naver Blog Writer" \
  --version 0.1.1 \
  --changelog "Add ACP marketplace-connected scripts (.sh) for preflight/setup_runner/publish"
```

## Post-publish

- [ ] `clawhub install naver-writer-acp --version 1.1.0` works in clean dir
- [ ] Installed scripts run (`scripts/smoke_test.sh`)
