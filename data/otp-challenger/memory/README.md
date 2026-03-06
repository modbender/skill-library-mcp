# OTP Memory Directory - Development/Testing

This `memory/` directory within the skill directory serves as a **development and testing workspace** for the OTP Challenger skill.

## Purpose

- **Development**: Local testing of OTP state file handling during skill development
- **Testing**: Temporary storage for test OTP configurations and verification data
- **Isolation**: Keeps development artifacts separate from runtime state

## Important Distinction

This directory is **NOT** used during normal skill execution. The OTP scripts use a separate runtime directory:

- **Development directory** (this): `~/devel/openclaw/skills/otp/memory/`
- **Runtime directory**: `$HOME/.openclaw/memory/` (or `$OPENCLAW_WORKSPACE/memory/`)

## Security

- **Permissions**: 700 (owner-only access) for security of OTP-related data
- **Contents**: Should only contain development/testing artifacts
- **Cleanup**: Safe to clear contents during development iterations

## Runtime Behavior

When users run the OTP skill commands (`verify.sh`, `check-status.sh`, etc.), the scripts automatically:
1. Create state files at `$WORKSPACE/memory/otp-state.json`
2. Use `$HOME/.openclaw/memory/` as the default workspace
3. Maintain audit logs at the runtime location

This separation ensures development work doesn't interfere with production OTP state management.
