---
name: totp
description: TOTP-based OTP verification for sensitive operations (env vars, gateway restarts, backup deletions, critical config changes). Uses otplib with window:2 (1 minute tolerance).
metadata:
  {
    "openclaw": {
      "requires": { "env": ["TOTP_SECRET"], "bins": ["node"] },
      "primaryEnv": "TOTP_SECRET",
      "emoji": "🔐"
    }
  }
---

# TOTP Verification Skill

Secure OTP verification using TOTP (Time-based One-Time Password) for sensitive operations.

## Purpose

Protect access to:
- `.env` variables
- `openclaw.json` configuration
- Gateway restarts
- Backup deletions
- Critical configuration changes
- External API key operations

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Generate secret and QR:**
   ```bash
   npm run generate
   ```
   Optionally pass service and account name:
   ```bash
   node scripts/generate-secret.js MyService myuser
   ```

3. **Send the QR image** (`qr.png`) to the user, then delete it immediately:
   ```bash
   rm qr.png
   ```

4. **Set TOTP_SECRET in `.env`:**
   ```env
   TOTP_SECRET=YOUR_BASE32_SECRET_HERE
   ```

5. **Configure Google Authenticator/Authy** with the generated secret or QR.

## Usage

When a sensitive operation is requested:

1. **Agent:** "Please provide your OTP"
2. **User:** Provides 6-digit code from authenticator app
3. **Agent:** Runs verification:
   ```bash
   TOTP_SECRET=$TOTP_SECRET node scripts/verify.js 123456
   ```
4. **If valid (exit 0):** Proceed with operation
5. **If invalid (exit 1):** Deny access

## Files

- `scripts/generate-secret.js` - Generate new TOTP secret and QR
- `scripts/verify.js` - Verify OTP tokens (window:2 = 1 minute tolerance)
- `SKILL.md` - This documentation

## Security Notes

- **Window:** 2 (1 minute tolerance) for time drift
- **Algorithm:** SHA1
- **Digits:** 6
- **Period:** 30 seconds
- **Secret:** Base32 encoded, stored in `.env` as `TOTP_SECRET`

## Integration

This skill should be integrated into the agent's decision flow when:
1. User requests `.env` variables
2. User requests `openclaw.json` contents
3. User requests gateway restart
4. User requests backup deletion
5. Any operation marked as "critical"
