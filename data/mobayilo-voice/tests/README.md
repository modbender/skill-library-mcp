# Tests

Run from integration root:

```bash
cd integrations/mobayilo_voice
PYTHONPATH=. python3 -m pytest -q tests/test_adapter.py
```

Coverage focus:
- host guardrail behavior
- masking and privacy behavior
- warning-only update checks
- approval gating behavior
- destination guardrails
