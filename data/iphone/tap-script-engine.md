# Tap Script Engine

Use this format so the user feels live operator control.

## Script Format

For each mission step, provide:

1. **Path:** exact route in Settings or app.
2. **Action:** the specific toggle, option, or button.
3. **Expected signal:** what success should look like.
4. **If not:** immediate branch step.

## Example Block

- **Path:** Settings -> Battery -> Battery Health & Charging
- **Action:** Confirm whether Optimized Battery Charging is enabled
- **Expected signal:** toggle is on and no severe service warning
- **If not:** enable it, then run a one-hour drain observation check

## Timing Discipline

- Keep each step under 30-60 seconds when possible.
- Re-check state after every major toggle change.
- If two consecutive steps fail, switch to rescue ladder.

## Language Style

- Use direct action verbs.
- Keep one action per line.
- Avoid abstract tips during active troubleshooting.
