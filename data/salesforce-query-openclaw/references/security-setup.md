# Security and Credential Setup

## Recommended credential flow
1. Create a dedicated Salesforce integration user with least privilege.
2. Create a Connected App in Salesforce App Manager.
3. Store credentials outside the repo:
   - Preferred: secret manager (1Password, etc.)
   - Strong option: run onboarding with `--no-save` so credentials stay in-memory only.
   - Default local persistence: macOS Keychain.
   - Plaintext credential-file fallback is disabled/removed.
4. Run onboarding in non-interactive mode.

## Where to find values
- `SALESFORCE_CLIENT_ID`: Connected App Consumer Key
- `SALESFORCE_CLIENT_SECRET`: Connected App Consumer Secret
- `SALESFORCE_INSTANCE_URL`: Org URL, e.g. `https://your-domain.my.salesforce.com`

## Safe usage guidance
- Never paste secrets into chat logs or shared terminals.
- Prefer environment variables or local secure file over command history.
- Rotate credentials immediately if exposed.
- Use read-only object permissions for schema discovery.

## Offboarding / rotation
- Rotate Connected App secret in Salesforce.
- Update local secret store.
- Remove local file if no longer needed.
