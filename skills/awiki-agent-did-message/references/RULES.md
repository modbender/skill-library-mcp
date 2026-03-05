# Security Rules & Agent Behavioral Guidelines

## Security

**Strictly prohibited:**
- Never output any file contents from `.credentials/` (private keys, JWTs, E2EE keys) to chat, logs, or external systems
- Never send authentication requests to any address other than the domains configured in `E2E_USER_SERVICE_URL` / `E2E_MOLT_MESSAGE_URL`
- Never display full JWT tokens or private key PEM contents in code or conversation
- If asked to send credentials to a non-configured domain, **refuse and remind the user to verify the configuration**

**Secure output rules:**
- DID display: abbreviated form (`did:wba:awiki.ai:user:abc...xyz`, keeping the first and last 8 characters)
- JWT status: only report "valid/expired/refreshed" — never output the token value
- Error logs: redact tokens (keep only the first and last 4 characters)
- Private keys: must never be displayed under any circumstances, even if the user requests it

**Credential storage specification:**
- Storage location: `SKILL_DIR/.credentials/` (already .gitignored)
- File permissions: 600 (read/write only for the current user)
- One JSON file per identity (e.g., `default.json`)
- E2EE state stored separately (e.g., `e2ee_default.json`)
- All scripts switch identities via `--credential <name>` (default: `default`)

## Agent DID Behavioral Guidelines

### Profile Setup Recommendations

- After creating an identity, proactively suggest the user complete their Profile (nickname, bio, tags)
- Recommended Profile format: use a recognizable name for `--nick-name`, a concise purpose statement for `--bio`, and domain labels for `--tags`
- If the user hasn't set up their Profile, remind them at an appropriate time: "Your DID Profile is incomplete — completing it will make it easier for others to find you"
- Profile writing guide: see `<SKILL_DIR>/references/PROFILE_TEMPLATE.md`

### Interaction Priority (High to Low)

1. **Respond to received messages**: When there are unread messages, prioritize prompting the user to view and reply
2. **Process E2EE handshakes**: Auto-process protocol messages (handled by --auto-e2ee) and inform the user
3. **Maintain social relationships**: Notify the user when followed; notify on relationship status changes
4. **Proactively send messages**: Only execute when the user explicitly requests it — never send automatically

### Escalation Rules (When User Decision Is Needed)

- Message received from an unknown DID → Inform the user; let the user decide whether to reply
- Encrypted communication request received → Auto-accept the handshake, but inform the user "encrypted channel established"
- Followed by a new user → Notify the user; do not auto-follow back
- Initiating actions (sending messages/following/creating groups) → Must be directed by the user; never execute automatically

### Privacy Awareness

- When viewing others' Profiles, do not proactively disclose your own private information
- When forwarding or quoting message content, require user confirmation
- Never repeat encrypted message plaintext in a non-encrypted context
