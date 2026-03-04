# Security and Troubleshooting

## Credential rules

- Use **least-privilege, bucket-scoped** credentials. See per-provider guide for exact policy.
- Prefer short-lived or scoped keys over account-wide admin keys.
- Never commit credentials to git.
- Rotate immediately if you suspect leakage.
- `~/.openclaw/openclaw.json` should be `600` — readable only by the owning user.

## Encryption

Set `config.encrypt=true` to GPG-encrypt archives before upload.

- Set `env.GPG_PASSPHRASE` for automated (non-interactive) encryption/decryption.
- Without it, GPG prompts interactively (won't work in cron).

## Restore safety

1. Always `restore --dry-run` first — lists contents without extracting.
2. Archives are SHA-256 checksummed on create and verified on restore (local and cloud).
3. Tar paths are validated — absolute paths and `..` traversal are rejected.
4. Non-interactive restore requires `--yes` (prevents accidental overwrites).

## Troubleshooting

### `Unable to locate credentials`

Credentials not configured. Set `env.ACCESS_KEY_ID` + `env.SECRET_ACCESS_KEY`, or `config.profile`.

### `AccessDenied`

Credentials lack required permissions. Check the IAM policy / API token scope covers `ListBucket`, `GetObject`, `PutObject`, `DeleteObject` for the target bucket.

### `SignatureDoesNotMatch`

Usually a region mismatch. Ensure `config.region` matches the provider's actual region. Also check system clock is correct.

### `Could not connect to the endpoint URL`

- Wrong or missing `config.endpoint`.
- AWS S3: leave endpoint unset.
- All other providers: endpoint is required.

### Checksum mismatch on restore

Archive may be corrupted or tampered. Re-download and retry. If persistent, check bucket storage integrity.

## Incident response

1. Revoke compromised key immediately in provider console.
2. Create new scoped credentials.
3. Update `skills.entries.cloud-backup.env.*` via `gateway config.patch`.
4. Audit recent bucket activity.
5. Run a fresh backup with new credentials.
