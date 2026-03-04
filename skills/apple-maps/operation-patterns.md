# Operation Patterns - Apple Maps (MacOS)

Use these patterns to keep behavior deterministic and auditable.

## Place Search Pattern

1. Confirm search query text.
2. Ask for area context if the request is ambiguous.
3. Build URL with `q` and optional `near`.
4. Show preview URL and launch with `open -a Maps`.
5. Confirm expected result type after launch.

## Nearby Category Pattern

1. Normalize category term (for example "restaurants", "pharmacy", "parking").
2. Confirm target area (city, neighborhood, or coordinates).
3. Build URL with `q` category and `near` area.
4. Launch and summarize what the user should see.

## Route Pattern

1. Confirm origin (`saddr`) and destination (`daddr`).
2. Confirm route mode (`dirflg`: driving, walking, transit).
3. Build URL and show preview before launch.
4. Launch in Maps and verify mode/destination match intent.

## Share-Link Pattern

1. Generate and display final map URL.
2. Confirm explicit approval before sharing externally.
3. Log share confirmation and minimal context in safety logs.

## Bulk Candidate Pattern

1. Provide shortlist in text before any launch.
2. Ask user to pick one or approve opening multiple links.
3. For more than one link, require second explicit confirmation.
4. Report which links were opened.

## Failure Pattern

- If Maps opens but result is off-target, refine parameters and relaunch once.
- If command path fails, switch to next valid path and state capability changes.
- If no safe path exists, stop and provide one actionable fix.
