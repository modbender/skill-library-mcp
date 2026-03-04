# Install & Runtime Source (Pinned)

This ClawHub package is text-only. Use the pinned GitHub release for runnable code.

## Trusted runtime source

- Repository: https://github.com/con2000us/zenTable
- Pinned release: https://github.com/con2000us/zenTable/releases/tag/skillhub-zentable-beta-2026-03-01

## Safety-first install flow

1. Download the pinned release assets from the URL above.
2. Review key scripts before execution:
   - `skills/zentable/table_renderer.py`
   - `scripts/zentable_render.py`
3. Install dependencies in a controlled environment.
4. Run smoke test.

## Smoke test (from repository root)

```bash
python3 -m py_compile scripts/zentable_render.py

echo '{"headers":["A","B"],"rows":[["1","2"]]}' \
| python3 skills/zentable/table_renderer.py - /tmp/zt_smoke.png --theme minimal_ios_mobile --width 450

ls -lh /tmp/zt_smoke.png
```

## Operational guidance

- For first-time setup/execution, require explicit user confirmation.
- Prefer sandbox/VM/container when evaluating in sensitive environments.
