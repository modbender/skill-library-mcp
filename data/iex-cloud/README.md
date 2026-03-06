# iex-cloud-skill

OpenClaw skill for using the IEX Cloud API.

## Provenance

- Homepage: https://github.com/oscraters/iex-cloud-skill
- Source repository: https://github.com/oscraters/iex-cloud-skill.git

The registry-facing metadata for this skill lives in `registry-metadata.json`.
The OpenClaw-facing metadata source of truth lives in the `SKILL.md` frontmatter.

## Credentials and Secrets

Preferred credential:

- `IEX_TOKEN`

Compatibility alias:

- `IEX_CLOUD_TOKEN`

Optional configuration:

- `IEX_BASE_URL`

For OpenClaw, prefer storing the token at `skills.entries.iex-cloud.apiKey` and backing it with a SecretRef using:

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

For direct shell use outside OpenClaw, export `IEX_TOKEN` in your shell.

## Runtime Requirements

- `curl` required
- `jq` optional for pretty JSON

## Security Guardrails

- The CLI uses query-parameter authentication because that matches the provider API.
- Base URL overrides are allowed only for trusted IEX API hosts.
- If a trusted custom base URL is used, the CLI prints a warning so the override is visible.
- `raw` requests accept only relative API paths and reject full URLs.
- Do not provide production tokens until you have reviewed the code and configuration you plan to run.

## Validation

Run the local metadata check with:

```bash
python3 scripts/validate_registry_metadata.py
```

This check verifies that `SKILL.md`, `registry-metadata.json`, and the runtime contract in `scripts/iex_cloud_cli.sh` stay aligned.
