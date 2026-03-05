# agent-skill-wallabag

A lightweight AI-agent skill for interacting with the [Wallabag](https://www.wallabag.org/) API.

It supports OAuth authentication and common bookmark operations:

- create entries
- list and search entries
- read a single entry
- update entry metadata
- delete entries
- add/remove tags

## Requirements

- required: `bash`, `curl`
- required for tag operations (`tag add`, `tag remove`): `jq`

## Environment Variables

Set these before running the script:

- `WALLABAG_BASE_URL`
- `WALLABAG_CLIENT_ID`
- `WALLABAG_CLIENT_SECRET`
- `WALLABAG_USERNAME`
- `WALLABAG_PASSWORD`

Example:

```bash
export WALLABAG_BASE_URL="https://wallabag.example.com"
export WALLABAG_CLIENT_ID="your-client-id"
export WALLABAG_CLIENT_SECRET="your-client-secret"
export WALLABAG_USERNAME="your-username"
export WALLABAG_PASSWORD="your-password"
```

## CLI Usage

Main command:

```bash
scripts/wallabag.sh <subcommand> [options]
```

Subcommands:

- `auth [--show-token]`
- `list [--search <text>] [--tag <name>] [--archive 0|1] [--starred 0|1] [--page <n>] [--per-page <n>]`
- `get --id <entry_id>`
- `create --url <url> [--title <title>] [--tags "tag1,tag2"]`
- `update --id <entry_id> [--title <title>] [--tags "tag1,tag2"] [--archive 0|1] [--starred 0|1]`
- `delete --id <entry_id>`
- `tag add --id <entry_id> --tags "tag1,tag2"`
- `tag remove --id <entry_id> --tag "tag"`

## Quick Example

```bash
# verify credentials (safe output, token not printed)
./scripts/wallabag.sh auth

# create bookmark
./scripts/wallabag.sh create --url "https://example.com" --tags "ai,read-later"

# find bookmark
./scripts/wallabag.sh list --search "example"
```

## Security Notes

- Do not commit credentials.
- Keep secrets in environment variables.
- OAuth password grant requires full account credentials; use a dedicated low-privilege account where possible.
- Tokens are held in-process only and are not persisted to disk.
- `auth --show-token` prints token JSON to stdout; use it only in secure, non-logged sessions.

## References

- Wallabag OAuth docs: https://doc.wallabag.org/developer/api/oauth/
- Wallabag API docs: https://app.wallabag.it/api/doc/
