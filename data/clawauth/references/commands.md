# Clawauth Commands (Agent Reference)

## Prerequisite

- `clawauth` is expected to be preinstalled by the operator in a trusted runtime image.
- OpenClaw metadata in `SKILL.md` declares `requires.bins` and an install action for the CLI.
- If the binary is missing, OpenClaw/Gateway should resolve this via the metadata install action (not ad-hoc agent shell install steps).

Manual fallback:

```bash
npm i -g clawauth
clawauth --help
```

## Discover providers

```bash
clawauth providers --json
```

## Start async auth

```bash
clawauth login start <provider> --json
```

Key fields from output:

- `sessionId`
- `shortAuthUrl`
- `expiresIn`
- `statusCommand`
- `claimCommand`

## Check status later

```bash
clawauth login status <sessionId> --json
```

Status values:

- `pending`
- `completed`
- `error`

## Claim completed session

```bash
clawauth login claim <sessionId> --json
```

On `completed`, output includes token payload and keychain storage metadata.

## Optional blocking mode

```bash
clawauth login wait <sessionId> --json
```

## Recover lost context

```bash
clawauth sessions --json
```

```bash
clawauth session-rm <sessionId> --json
```

## Token retrieval

```bash
clawauth token list --json
```
Security note:

- This skill intentionally avoids commands that materialize raw tokens into output/environment.

## Detailed manual

```bash
clawauth explain
```
