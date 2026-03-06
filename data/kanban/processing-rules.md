# Processing Rules - Kanban

Use this deterministic flow whenever the user asks what to do next or requests board updates.

## Card Selection Order

1. Blocked cards that unblock highest-impact downstream work
2. Ready cards sorted by priority (P0 > P1 > P2 > P3)
3. Cards closest to due date
4. Oldest cards in ready queue

If tie remains, prefer the smallest executable task.

## State Transition Rules

- `backlog -> ready`: requirements are clear and owner is known
- `ready -> in-progress`: WIP limit allows it
- `in-progress -> review`: implementation complete with validation artifact
- `review -> done`: acceptance criteria explicitly met
- `any -> blocked`: blocker identified and recorded
- `blocked -> ready`: blocker resolved and evidence logged

## WIP Enforcement

- Read limits from `board.md` or `rules.md`.
- If target lane is full, do not move cards into it.
- Suggest the highest-value card to finish first to free capacity.

## Update Procedure

1. Load board using `discovery-protocol.md`.
2. Compute intended transition and validate against rules.
3. Apply the board update.
4. Append matching log row with timestamp and rationale.
5. Report final board delta to user.

## Conflict Handling

- If two instructions conflict, ask for priority override.
- If a card appears duplicated, keep the oldest ID and merge notes.
- If owner is unknown, set `owner` to `unassigned` and flag for assignment.
