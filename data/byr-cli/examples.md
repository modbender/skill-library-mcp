# Examples

## Search

```bash
byr search --query "ubuntu" --limit 5 --json
```

## Browse

```bash
byr browse --limit 20 --category movie --spstate free --json
```

## Search by IMDb

```bash
byr search --imdb tt0133093 --category movie --spstate free --json
```

## Get detail

```bash
byr get --id 1001 --json
```

## Download dry-run

```bash
byr download --id 1001 --output ./1001.torrent --dry-run --json
```

## Download write

```bash
byr download --id 1001 --output ./1001.torrent --json
```

## User info

```bash
byr check --json
byr whoami --json
byr doctor --verify --json
byr user info --json
```

## Metadata

```bash
byr meta categories --json
byr meta levels --json
```

## Auth lifecycle

```bash
byr auth status --verify --json
byr auth import-cookie --cookie "uid=...; pass=..." --json
byr auth import-cookie --cookie "session_id=...; auth_token=...; refresh_token=..." --json
byr auth import-cookie --from-browser chrome --profile "Default" --json
byr auth logout --json
```
