# EVE ESI Character Endpoints Reference

Base URL: `https://esi.evetech.net/latest`

All authenticated endpoints require `Authorization: Bearer <TOKEN>` header. Replace `{character_id}` with the numeric character ID from SSO verify.

## Table of Contents

- [Character Info](#character-info)
- [Wallet](#wallet)
- [Assets](#assets)
- [Skills](#skills)
- [Clones and Implants](#clones-and-implants)
- [Location](#location)
- [Contacts](#contacts)
- [Contracts](#contracts)
- [Calendar](#calendar)
- [Fittings](#fittings)
- [Industry](#industry)
- [Killmails](#killmails)
- [Mail](#mail)
- [Market Orders](#market-orders)
- [Mining](#mining)
- [Notifications](#notifications)
- [Loyalty Points](#loyalty-points)
- [Planets (PI)](#planets-pi)
- [Blueprints](#blueprints)
- [Roles and Titles](#roles-and-titles)
- [Standings](#standings)
- [Bookmarks](#bookmarks)
- [Medals](#medals)
- [Agent Research](#agent-research)
- [Fatigue](#fatigue)
- [Faction Warfare](#faction-warfare)
- [Corporation History](#corporation-history)
- [Portrait](#portrait)
- [Search](#search)
- [Fleet](#fleet)

---

## Character Info

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/` | -- | Public character info (name, corp, birthday, etc.) |
| GET | `/characters/{character_id}/online/` | `esi-location.read_online.v1` | Online status, last login/logout |
| POST | `/characters/affiliation/` | -- | Bulk lookup corp/alliance/faction for character IDs |

## Wallet

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/wallet/` | `esi-wallet.read_character_wallet.v1` | ISK balance |
| GET | `/characters/{character_id}/wallet/journal/` | `esi-wallet.read_character_wallet.v1` | Wallet journal (paginated) |
| GET | `/characters/{character_id}/wallet/transactions/` | `esi-wallet.read_character_wallet.v1` | Wallet transactions |

## Assets

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/assets/` | `esi-assets.read_assets.v1` | All assets (paginated) |
| POST | `/characters/{character_id}/assets/locations/` | `esi-assets.read_assets.v1` | Locations for specific item IDs |
| POST | `/characters/{character_id}/assets/names/` | `esi-assets.read_assets.v1` | Names for specific item IDs |

## Skills

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/skills/` | `esi-skills.read_skills.v1` | All trained skills + total SP |
| GET | `/characters/{character_id}/skillqueue/` | `esi-skills.read_skillqueue.v1` | Current skill queue |
| GET | `/characters/{character_id}/attributes/` | `esi-skills.read_skills.v1` | Character attributes (int, mem, etc.) |

## Clones and Implants

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/clones/` | `esi-clones.read_clones.v1` | Jump clones and home location |
| GET | `/characters/{character_id}/implants/` | `esi-clones.read_implants.v1` | Active implant type IDs |

## Location

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/location/` | `esi-location.read_location.v1` | Current solar system, station/structure |
| GET | `/characters/{character_id}/ship/` | `esi-location.read_ship_type.v1` | Current ship type and name |

## Contacts

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/contacts/` | `esi-characters.read_contacts.v1` | Contact list |
| POST | `/characters/{character_id}/contacts/` | `esi-characters.write_contacts.v1` | Add contacts |
| PUT | `/characters/{character_id}/contacts/` | `esi-characters.write_contacts.v1` | Edit contacts |
| DELETE | `/characters/{character_id}/contacts/` | `esi-characters.write_contacts.v1` | Delete contacts |
| GET | `/characters/{character_id}/contacts/labels/` | `esi-characters.read_contacts.v1` | Contact labels |

## Contracts

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/contracts/` | `esi-contracts.read_character_contracts.v1` | All contracts (paginated) |
| GET | `/characters/{character_id}/contracts/{contract_id}/bids/` | `esi-contracts.read_character_contracts.v1` | Bids on a contract |
| GET | `/characters/{character_id}/contracts/{contract_id}/items/` | `esi-contracts.read_character_contracts.v1` | Items in a contract |

## Calendar

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/calendar/` | `esi-calendar.read_calendar_events.v1` | Upcoming events (50 max) |
| GET | `/characters/{character_id}/calendar/{event_id}/` | `esi-calendar.read_calendar_events.v1` | Event details |
| GET | `/characters/{character_id}/calendar/{event_id}/attendees/` | `esi-calendar.read_calendar_events.v1` | Event attendees |
| PUT | `/characters/{character_id}/calendar/{event_id}/` | `esi-calendar.respond_calendar_events.v1` | Respond to event |

## Fittings

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/fittings/` | `esi-fittings.read_fittings.v1` | Saved fittings |
| POST | `/characters/{character_id}/fittings/` | `esi-fittings.write_fittings.v1` | Create a fitting |
| DELETE | `/characters/{character_id}/fittings/{fitting_id}/` | `esi-fittings.write_fittings.v1` | Delete a fitting |

## Industry

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/industry/jobs/` | `esi-industry.read_character_jobs.v1` | Industry jobs (manufacturing, research, etc.) |

## Killmails

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/killmails/recent/` | `esi-killmails.read_killmails.v1` | Recent killmail IDs + hashes |
| GET | `/killmails/{killmail_id}/{killmail_hash}/` | -- | Full killmail details (public) |

## Mail

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/mail/` | `esi-mail.read_mail.v1` | Mail headers (paginated) |
| GET | `/characters/{character_id}/mail/{mail_id}/` | `esi-mail.read_mail.v1` | Single mail body |
| POST | `/characters/{character_id}/mail/` | `esi-mail.send_mail.v1` | Send a mail |
| PUT | `/characters/{character_id}/mail/{mail_id}/` | `esi-mail.organize_mail.v1` | Update labels / mark read |
| DELETE | `/characters/{character_id}/mail/{mail_id}/` | `esi-mail.organize_mail.v1` | Delete a mail |
| GET | `/characters/{character_id}/mail/labels/` | `esi-mail.read_mail.v1` | Mail labels + unread counts |
| POST | `/characters/{character_id}/mail/labels/` | `esi-mail.organize_mail.v1` | Create mail label |
| GET | `/characters/{character_id}/mail/lists/` | `esi-mail.read_mail.v1` | Mailing lists |

## Market Orders

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/orders/` | `esi-markets.read_character_orders.v1` | Active market orders |
| GET | `/characters/{character_id}/orders/history/` | `esi-markets.read_character_orders.v1` | Expired/cancelled orders (paginated) |

## Mining

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/mining/` | `esi-industry.read_character_mining.v1` | Mining ledger (last 30 days) |

## Notifications

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/notifications/` | `esi-characters.read_notifications.v1` | All notifications |
| GET | `/characters/{character_id}/notifications/contacts/` | `esi-characters.read_notifications.v1` | Contact notifications |

## Loyalty Points

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/loyalty/points/` | `esi-characters.read_loyalty.v1` | LP balances per corp |

## Planets (PI)

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/planets/` | `esi-planets.manage_planets.v1` | List of colonies |
| GET | `/characters/{character_id}/planets/{planet_id}/` | `esi-planets.manage_planets.v1` | Colony layout and extractors |

## Blueprints

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/blueprints/` | `esi-characters.read_blueprints.v1` | All blueprints (paginated) |

## Roles and Titles

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/roles/` | `esi-characters.read_corporation_roles.v1` | Corporation roles |
| GET | `/characters/{character_id}/titles/` | `esi-characters.read_titles.v1` | Corporation titles |

## Standings

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/standings/` | `esi-characters.read_standings.v1` | NPC standings |

## Bookmarks

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/bookmarks/` | `esi-bookmarks.read_character_bookmarks.v1` | All bookmarks (paginated) |
| GET | `/characters/{character_id}/bookmarks/folders/` | `esi-bookmarks.read_character_bookmarks.v1` | Bookmark folders |

## Medals

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/medals/` | `esi-characters.read_medals.v1` | Awarded medals |

## Agent Research

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/agents_research/` | `esi-characters.read_agents_research.v1` | Research agents and points |

## Fatigue

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/fatigue/` | `esi-characters.read_fatigue.v1` | Jump fatigue expiry timestamps |

## Faction Warfare

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/fw/stats/` | `esi-characters.read_fw_stats.v1` | FW kill/VP stats |

## Corporation History

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/corporationhistory/` | -- | Public employment history |

## Portrait

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/portrait/` | -- | Portrait URLs (64/128/256/512px) |

## Search

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/search/` | `esi-search.search_structures.v1` | Authenticated search (includes structures) |

## Fleet

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/characters/{character_id}/fleet/` | `esi-fleets.read_fleet.v1` | Current fleet info |

---

## Pagination

Paginated endpoints return `X-Pages` header. Append `?page=N` (1-based). Always check `X-Pages` to determine total pages.

## Caching

Every response includes `Expires` and `Last-Modified` headers. Do not request again before `Expires`. Use `If-None-Match` with the `ETag` header for conditional requests (returns 304 if unchanged).

## Error Handling

- `403`: Missing scope or wrong character
- `404`: Resource not found
- `420`: Error rate limited (back off and retry)
- `502/503/504`: Upstream server issue (retry with backoff)
- Check `X-ESI-Error-Limit-Remain` and `X-ESI-Error-Limit-Reset` headers
