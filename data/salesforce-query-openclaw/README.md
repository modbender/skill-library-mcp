# Salesforce Query (Schema-Adaptive) Skill

We built this because the usual Salesforce scripts kept breaking between orgs.

One team has 6sense fields, another does not. One org tracks campaign engagement on leads in a custom way, another keeps everything on contacts. Hardcoded assumptions make tools brittle fast.

This skill takes the opposite approach. It discovers what exists in your org first, then builds a reusable profile so queries and workflows fit your schema instead of fighting it.

## Source code

- GitHub: https://github.com/RikH81/salesforce-query-openclaw-skill

## What it helps with

- Connecting to any Salesforce org via OAuth client credentials
- Discovering available objects and fields at runtime
- Building a reusable profile for account, contact, opportunity, campaign, and activity research
- Running starter GTM workflows for prioritization and outreach context

## Security model

Credentials are stored in macOS Keychain (service: `openclaw.salesforce`).

- No plaintext credential-file fallback
- Optional session-only mode via `--no-save`
- Designed to keep secrets out of repos and local text files

Required values:

- `SALESFORCE_CLIENT_ID`
- `SALESFORCE_CLIENT_SECRET`
- `SALESFORCE_INSTANCE_URL`

## Quick start

Interactive onboarding:

```bash
python3 scripts/onboarding.py
```

Non-interactive onboarding:

```bash
python3 scripts/onboarding.py \
  --client-id "$SALESFORCE_CLIENT_ID" \
  --client-secret "$SALESFORCE_CLIENT_SECRET" \
  --instance-url "$SALESFORCE_INSTANCE_URL" \
  --non-interactive
```

Session-only credentials (do not persist):

```bash
python3 scripts/onboarding.py \
  --client-id "$SALESFORCE_CLIENT_ID" \
  --client-secret "$SALESFORCE_CLIENT_SECRET" \
  --instance-url "$SALESFORCE_INSTANCE_URL" \
  --non-interactive --no-save
```

## Check credential setup

```bash
python3 scripts/credential_doctor.py
```

Expected result:

- all three Salesforce credential keys present in Keychain

## Practical notes before production

- Use a dedicated least-privilege Salesforce integration user
- Rotate client secrets if exposed
- Keep org-specific sensitive mappings out of public repos

## Why this exists

If you have ever copied a "works for my org" Salesforce script and watched it fail in another environment, this is for you. The goal is simple: get useful GTM research outputs without rewriting your tooling every time schema reality changes.
