# Gate: Behavior Capture + Deterministic Replay (REBUILD mode only)

**Question:** Does the new code behave identically to the old code?

## Process

**Before touching anything:**
1. Record all inputs → outputs from existing codebase (API calls, function returns, CLI outputs)
2. Save as golden fixtures in `.wreckit/golden/`

**After rebuilding:**
3. Replay all golden fixtures through the new code
4. Diff outputs

## Pass/Fail

- **Pass:** Identical outputs for all captured inputs (or documented, justified differences).
- **Fail:** Any unexpected output difference.
