# Bitwarden/Vaultwarden setup checklist (OpenClaw)

## Done automatically
- `bw` CLI installed
- server configured
- safe wrapper skill created (`vw_cli.py`)

## Still required from Maxime (once)
1. Create these Vaultwarden items (Login type, password field used):
   - `oc-bw-clientid` -> value = BW_CLIENTID
   - `oc-bw-clientsecret` -> value = BW_CLIENTSECRET
   - `oc-bw-password` -> value = account master password
2. In shell (root):
   - `bw login --apikey`
   - `bw unlock` then export `BW_SESSION`
3. Test helper:
   - `cd skills/bitwarden-secrets`
   - `./scripts/vw_env_export.sh > /tmp/vw_exports.sh`
   - `source /tmp/vw_exports.sh`
4. Validate:
   - `python3 scripts/vw_cli.py sync`
   - `python3 scripts/vw_cli.py search --query google`
5. Lock when done:
   - `bw lock`

## Notes
- Never paste secrets/BW_SESSION into Discord.
- Reveal mode exists but requires explicit confirmation token.
