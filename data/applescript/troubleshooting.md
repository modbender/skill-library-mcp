# Troubleshooting

Use this sequence when AppleScript execution fails.

## 1. Capture Exact Failure

Collect:
- Full `osascript` command used
- Exact stderr message
- Target app and intended action

Avoid generic retry loops before root-cause checks.

## 2. Permission and Automation Access

- Verify Automation permission prompts were accepted.
- Re-run a minimal read-only probe.
- If blocked, guide user to system privacy settings.

## 3. Dictionary Mismatch

- Re-check class and property names in the app dictionary.
- Confirm app version-specific differences.
- Replace guessed properties with verified ones.

## 4. Timing and App State

- Ensure target app is open and ready.
- Add bounded wait/retry for startup race conditions.
- Avoid long unbounded delays.

## 5. Data and Quoting Issues

- Test with safe sample input.
- Escape quotes and special characters deterministically.
- Verify list delimiters and string concatenation behavior.

## 6. Recovery Output

Report:
- Root cause category
- Next command to run
- Safer fallback if primary approach remains blocked
