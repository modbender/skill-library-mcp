# BitNote Ops Runbook

## Preflight

1. Confirm ABI freshness (`node scripts/getAbi.mjs`).
2. Confirm target username resolves to expected address.
3. Confirm wallet/account path is correct for the target profile.
4. Confirm request-id strategy for idempotency.

## Identity Continuity Workflow (SOUL.md-safe)

1. Extract the identity block to persist (full or partial `SOUL.md`).
2. Write as `Agent Identity Core` with stable request-id (e.g., `identity-core-v3`).
3. Verify `READ_AFTER_WRITE_OK 1`.
4. Retry with same request-id if network failure occurs.
5. Rotate to a new request-id only when content intentionally changes.

## Success Criteria

A successful write run must include:
- `TX_HASH`
- `NOTE_INDEX`
- `READ_AFTER_WRITE_OK 1`

A successful share-link generation run must include:
- `SENDER_USERNAME`
- `RECIPIENT_USERNAME`
- `SHARE_LINK`

## Failure Handling

- `IDEMPOTENT_HIT`: safe duplicate retry detected; do not reissue with new request-id unless content changed.
- `DECRYPTED_KEY_ADDRESS_MISMATCH`: wrong credentials/passphrase.
- `USERNAME_NOT_FOUND`: profile/username mismatch.
- `READ_AFTER_WRITE_OK 0`: treat as failed write; retry same request-id.
- `SENDER_USERNAME_NOT_FOUND`: sender username does not resolve on-chain.
- `RECIPIENT_USERNAME_NOT_FOUND`: recipient username does not resolve on-chain.
- Share link opens but fails to decrypt: verify exact recipient username case and regenerate using `scripts/generateShareLink.mjs` (do not handcraft `sm`/`st`).

## Security

- Use passphrases with at least **256 bits of entropy**.
- Keep passphrases in env/secret manager, never in committed files.
- Keep profile JSON free of secrets.
- Redact private details in shared logs.
