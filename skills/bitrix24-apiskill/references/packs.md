# Capability Packs

This skill stays thin by default and expands safely via packs.

## Token-Efficient Loading Order

Use this exact order:

1. Open this file (`packs.md`).
2. Open one `catalog-<pack>.md`.
3. Open `chains-<pack>.md` only if workflow detail is needed.
4. Open `bitrix24.md` only for protocol-level troubleshooting.

Context budget:

- default: max 2 files before first action,
- max 1 active pack unless task explicitly spans multiple domains,
- keep `core` as default pack.

## Packs

- `core`: crm + tasks.task + user + events + batch
- `comms`: chats, chat-bots, notifications, telephony
- `automation`: bizproc, robots, workflow templates
- `collab`: workgroups, social feed, collaboration layer
- `content`: disk/files/document flows
- `boards`: scrum/board flows
- `commerce`: orders, payments, deliveries, product catalog
- `services`: booking, calendar, time-management
- `platform`: ai, entity storage, biconnector data layer
- `sites`: landing/site/page operations
- `compliance`: user consents and sign-b2e document tails
- `diagnostics`: method availability, scopes, features, event catalog checks

## Runtime usage

- Default pack: `core`
- Add packs for a call: `--packs core,comms`
- Set global packs: `B24_PACKS="core,commerce"`
- Disable packs and use only explicit allowlist: `--packs none --method-allowlist 'user.*'`

## Design rules for new pack entries

1. Add only frequent methods.
2. Keep high-risk write methods explicit and documented.
3. Include at least one read-first chain before write chain.
4. Link every method to official docs.
5. Keep each catalog short; move detail to chains.
