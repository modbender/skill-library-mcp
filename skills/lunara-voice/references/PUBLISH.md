# Lunara Voice Bundle — Publish Guide

## 1) Publish/update plugin to npm (optional but recommended)

From plugin source directory:

```bash
cd /home/max/.openclaw/extensions/lunara-voice
npm login
npm publish --access public
```

## 2) Publish bundle to ClawHub

```bash
clawhub login
clawhub publish /home/max/.openclaw/clawhub-bundles/lunara-voice \
  --slug lunara-voice \
  --name "Lunara Voice" \
  --version 1.0.0 \
  --changelog "Initial bundle release" \
  --tags latest
```

## 3) Verify install flow as end-user

```bash
clawhub install lunara-voice --workdir /tmp/lunara-test --force
bash /tmp/lunara-test/skills/lunara-voice/scripts/install-plugin.sh
openclaw plugins info lunara-voice
openclaw plugins doctor
```

## Notes

- ClawHub stores skill bundles (files + metadata).
- Runtime OpenClaw plugin install still happens via `openclaw plugins install`.
- Keep plugin versioning in sync between `plugin/package.json` and `plugin/openclaw.plugin.json`.
