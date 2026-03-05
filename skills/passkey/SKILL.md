---
name: Passkey
description: Implement WebAuthn passkeys avoiding critical security and compatibility pitfalls.
metadata: {"clawdbot":{"emoji":"🔐","os":["linux","darwin","win32"]}}
---

## Security-Critical Rules
- Challenge must be unique per ceremony — reused challenges enable replay attacks
- Origin validation is mandatory — missing check allows phishing from similar domains
- Store and verify sign count — detects cloned authenticators when count doesn't increment
- Never implement CBOR parsing manually — use established libraries, crypto is hard

## Server Implementation
- Use battle-tested libraries — SimpleWebAuthn (JS), py_webauthn (Python), webauthn-rs (Rust)
- Challenges expire quickly — 60-120 seconds max, store server-side
- Store credential ID as base64 — binary data, needs encoding for database
- Store public key in COSE format — libraries handle this, don't transform it

## Credential Storage Requirements
- Credential ID — unique identifier, used in allowCredentials
- Public key — COSE format, for signature verification
- Sign count — integer, increment check detects cloning
- Transports hint — helps browser suggest correct authenticator

## Registration Traps
- `userVerification: "required"` enforces biometric/PIN — "preferred" may skip verification
- Attestation usually unnecessary — requiring it reduces device compatibility
- Allow multiple passkeys per account — users have multiple devices
- Resident key capability varies — don't assume all authenticators support discoverable credentials

## Authentication Traps
- Empty allowCredentials enables discoverable credentials — but not all passkeys are discoverable
- Timeout too short frustrates users — 120 seconds minimum for cross-device flows
- Cross-device auth (QR code) adds latency — don't timeout during Bluetooth handshake

## User Experience
- Provide password fallback — not all users have passkey-capable devices
- Conditional UI (`mediation: "conditional"`) for autocomplete — passkeys appear in username field
- Clear messaging on registration — users don't understand "security key" terminology
- Account recovery path required — hardware loss shouldn't lock out account forever

## Platform Sync Behavior
- Apple iCloud Keychain syncs across Apple devices — but not to Android/Windows
- Google Password Manager syncs Android + Chrome — but not to Apple devices
- Windows Hello is TPM-backed, local by default — doesn't sync
- 1Password/Bitwarden provide cross-platform sync — broadest compatibility option

## Testing
- Chrome DevTools > Application > WebAuthn — simulate authenticators without hardware
- Virtual authenticators in CI — no physical keys needed for automated tests
- Test both resident and non-resident credentials — different flows
- Cross-browser testing essential — Safari, Chrome, Firefox implementations vary
