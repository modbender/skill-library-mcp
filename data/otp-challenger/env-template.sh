#!/bin/bash
# OpenClaw OTP Challenger Environment Variables Template
# Source this file or copy exports to your shell profile (~/.bashrc, ~/.zshrc, etc.)

# =============================================================================
# TOTP (Time-based One-Time Password) Configuration
# =============================================================================
# These are used for 6-digit authenticator app codes

# Base32-encoded TOTP secret (required for TOTP verification)
# Generate with: ./generate-secret.sh
export OTP_SECRET="YOUR_BASE32_SECRET_HERE"

# =============================================================================
# YubiKey OTP Configuration
# =============================================================================
# These are used for 44-character YubiKey OTP codes

# Yubico API Client ID (get from https://upgrade.yubico.com/getapikey/)
export YUBIKEY_CLIENT_ID="YOUR_CLIENT_ID_HERE"

# Yubico API Secret Key (base64-encoded, from same page as client ID)
export YUBIKEY_SECRET_KEY="YOUR_BASE64_SECRET_KEY_HERE"

# =============================================================================
# Optional OTP Settings
# =============================================================================

# Maximum failed attempts before rate limiting (default: 3)
export OTP_MAX_FAILURES=3

# How long verification remains valid in hours (default: 24)
export OTP_INTERVAL_HOURS=24

# Audit log file path (default: ~/.openclaw/memory/otp-audit.log)
export OTP_AUDIT_LOG="$HOME/.openclaw/memory/otp-audit.log"

# Script to run when failures occur or rate limits are hit (optional)
# export OTP_FAILURE_HOOK="/path/to/your/failure-handler.sh"

# OpenClaw workspace directory (usually auto-detected)
# export OPENCLAW_WORKSPACE="$HOME/.openclaw"

# OpenClaw config file path (usually auto-detected)
# export OPENCLAW_CONFIG="$HOME/.openclaw/config.yaml"

# =============================================================================
# Usage Examples
# =============================================================================

# To verify a TOTP code:
# ./verify.sh "username" "123456"

# To verify a YubiKey OTP:
# ./verify.sh "username" "cccccccccccccccccccccccccccccccccccccccccccc"

# To check current verification status:
# ./check-status.sh "username"

# To get current TOTP code (for testing):
# ./get-current-code.sh

# =============================================================================
# Security Notes
# =============================================================================

# 1. Keep your secrets secure:
#    - Never commit this file with real values to version control
#    - Use appropriate file permissions (chmod 600)
#    - Consider using a secrets manager in production

# 2. TOTP secrets must be base32-encoded (A-Z, 2-7, optional = padding)
#    Length: 16-128 characters

# 3. YubiKey secrets must be base64-encoded (get from Yubico API key page)

# 4. Both TOTP and YubiKey can be configured simultaneously
#    The system will auto-detect code type based on format:
#    - 6 digits = TOTP
#    - 44 ModHex characters = YubiKey OTP

# =============================================================================
# Example with Real Values (DO NOT COMMIT)
# =============================================================================

# export OTP_SECRET="JBSWY3DPEHPK3PXP"
# export YUBIKEY_CLIENT_ID="12345"
# export YUBIKEY_SECRET_KEY="dGhpcyBpcyBhIHRlc3Qga2V5"
# export OTP_MAX_FAILURES=5
# export OTP_INTERVAL_HOURS=12