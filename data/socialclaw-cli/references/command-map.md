# Command Map

Use this map to route intent to the most specific `social` command group.

## Primary Domain Mapping

| Intent category | Use this group | Typical first command |
| --- | --- | --- |
| Login, token, app scopes, auth health | `auth` | `social auth status` |
| Read profile/pages/media/feed data | `query` | `social query me --fields id,name` |
| Publish/schedule Facebook page content | `post` | `social post pages --set-default` |
| Instagram account/media/insights/comments | `instagram` | `social instagram accounts list` |
| WhatsApp messages/templates/phone checks | `whatsapp` | `social whatsapp phone-numbers list` |
| Ads account/campaign/ad set/insights/budget | `marketing` | `social marketing status` |
| Workspace operations and approvals | `ops` | `social ops alerts list --open` |
| Plan-first agent workflows | `agent` | `social agent --plan-only "<task>"` |
| Local web control plane | `gateway` or `studio` | `social gateway --open` |

## Secondary Groups (Reference-Only in v1)

Use these when the user asks explicitly:

- `accounts`: multi-profile management
- `batch`: job files (`json`/`csv`)
- `hub`: package registry commands
- `limits`: rate-limit checks
- `utils`: version/config helpers
- `integrations`: guided onboarding (for example WABA connect)
- `policy`: region policy and preflight
- `tui`: interactive terminal dashboard
- `chat`: conversational mode alias

## Routing Rules

1. Prefer the narrowest command group that fully addresses the request.
2. If one request spans multiple domains, split into ordered steps.
3. Start mixed requests with a read-only diagnostic:
   - `social doctor`
   - `social auth status`
4. Keep workspace/profile explicit when present:
   - `social --profile <profile> ...`
   - `social ops ... --workspace <workspace>`

## Suggested Slot Extraction

Extract these parameters from user intent before generating commands:

- `profile` or `workspace`
- API surface (`facebook`, `instagram`, `whatsapp`, `marketing`)
- resource IDs (`page-id`, `ad-account`, `campaign-id`, `phone-number-id`)
- time range (`last_7d`, custom ISO time windows)
- output mode (`--table`, `--json`, `--export`)
