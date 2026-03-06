---
name: verify-matrix-device
description: Verify and cross-sign the active Matrix device for one OpenClaw-managed account. Use when a user needs to repair trust for an OpenClaw Matrix device, confirm the current device is self-signed, or recover cross-signing with a recovery key.
metadata: {"openclaw":{"requires":{"bins":["node","npm"]},"emoji":"🔐"}}
---

# OpenClaw Matrix Device Verification

Use this skill when the user wants to verify the currently active Matrix device for an OpenClaw-managed account.

## Required Inputs

- `homeserver`: Matrix homeserver base URL.
- `username`: OpenClaw account id, full Matrix user id, or unique localpart.
- `recovery key`: the Matrix recovery key. Treat this as a secret.
- Optional: path to `openclaw.json` when it is not in the default location.

## Workflow

1. If any required input is missing, ask the user for it.
2. Ensure dependencies are installed in this skill folder. If `{baseDir}/node_modules/matrix-js-sdk` is missing, run `npm install --prefix {baseDir}`.
3. Run the verifier from this skill folder:
   `node {baseDir}/scripts/verify_matrix_device.mjs --homeserver "<homeserver>" --username "<username>"`
4. If the user gave a non-default config path, append:
   `--openclaw-json "<path>"`
5. Let the script prompt for the recovery key in the terminal. Do not pass the recovery key on the command line or in environment variables.
6. Report whether the device was already cross-signed or was signed successfully.

## Notes

- The skill uses the existing OpenClaw access token from `openclaw.json`; it does not create a helper Matrix device.
- The verifier signs the active device directly and confirms the signature server-side.
- Use a real TTY so the hidden recovery-key prompt works correctly.
- For local testing outside OpenClaw, `--access-token` bypasses `openclaw.json` and prompts for the Matrix user ID plus access token (`--direct` and `-t` are compatibility aliases).
- If the access token is missing, `--password` (or `-p`) can log in with the Matrix password and sign a specific target `device_id`, then log out the temporary helper session.
