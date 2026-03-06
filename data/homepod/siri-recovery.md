# HomePod Siri Recovery Map

Use this map when Siri hears the request but fails to execute the intended Home action.

## Failure Categories

| Symptom | Likely Cause | First Check |
|---------|--------------|-------------|
| "Working on that" then timeout | Service or permission path | Validate account and home permissions |
| Action runs on wrong room | Ambiguous naming | Normalize room and accessory names |
| Correct action but delayed | Hub or network contention | Check hub state and network congestion |
| Siri cannot find accessory | Discovery mismatch | Confirm accessory visibility in Home app |

## Recovery Sequence

1. Reproduce with a minimal command:
- Use one concise command targeting one accessory.

2. Validate naming clarity:
- Room and accessory names should be unique and short.
- Remove near-identical aliases in the same home.

3. Validate control path:
- Confirm the same action works manually in Home app.
- If manual action fails, fix accessory path before Siri tuning.

4. Validate account scope:
- Confirm the requesting user has control rights for the target home.
- Verify no stale shared-home invitation state.

5. Validate voice routing:
- Confirm the active HomePod received the command.
- If multiple HomePods heard the command, reduce ambiguity by location context.

## Regression Checks

- Repeat the exact command three times in normal household conditions.
- Test at least one command per frequently used room.
- Record pass and fail counts in automation notes for trend tracking.
