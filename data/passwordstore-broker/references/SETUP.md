# Installation and Initial Setup

This document is for one-time setup of `passwordstore-broker` protocol and tools.

## Official references

- https://www.passwordstore.org/
- https://www.passwordstore.org/#setting-it-up

## Required tools

- `pass`
- `gpg`
- `openssl`
- `python3`
- `qrencode` (required for PNG QR enrollment output)

## Install commands

### macOS (Homebrew)

```bash
brew install pass gnupg openssl python qrencode
```

### Debian/Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y pass gnupg2 openssl python3 qrencode
```

### Fedora/RHEL

```bash
sudo dnf install -y pass gnupg2 openssl python3 qrencode
```

### Arch Linux

```bash
sudo pacman -S --needed pass gnupg openssl python qrencode
```

## Initialize password store

1. Create a GPG key (if needed):

```bash
gpg --full-generate-key
```

2. Find key id/email:

```bash
gpg --list-secret-keys --keyid-format LONG
```

3. Initialize `pass`:

```bash
pass init "<your-gpg-key-id-or-email>"
```

4. Optional upstream recommendation:

```bash
pass git init
```

Notes:
- `pass init` accepts multiple recipients.
- Per-subfolder recipients are supported via `pass init -p <subfolder> <gpg-id>`.

## Verify base installation

```bash
pass --version
gpg --version
openssl version
python3 --version
qrencode --version
```

## Agent-driven TOTP enrollment setup

Run once on the machine where `passwordstore-broker` executes:

```bash
scripts/setup_totp_enrollment.py
```

Expected JSON output:

- `secret_file`: default `~/.passwordstore-broker/totp.secret`
- `otpauth_url`: fallback manual authenticator enrollment URL
- `qr_png_path`: default `~/.passwordstore-broker/totp-enroll.png`
- `setup_timestamp_file`: default `~/.passwordstore-broker/setup_completed_at.txt`
- `setup_completed_at`: initial setup timestamp (UTC ISO-8601)
- `provisioned`: `true` if secret was created, `false` if reused

Expected permissions/artifacts:

- `~/.passwordstore-broker` mode `0700`
- `~/.passwordstore-broker/totp.secret` mode `0600`
- `~/.passwordstore-broker/totp-enroll.png` mode `0600` (best effort)
- `~/.passwordstore-broker/setup_completed_at.txt` mode `0600`

Security rule:
- The TOTP secret is enrollment-only material. Do not share or retransmit `totp.secret` contents after initial setup.
- For the initial setup send the QR code image at `qr_png_path` (preferred) or the `otpauth_url` to the user for enrollment in their authenticator app.

## Failure handling

- Invalid/expired TOTP code: submission fails with authentication error.
- Too many failed TOTP attempts: temporary lockout is applied.
- Lockout policy: 5 failed attempts within 5 minutes causes 5-minute lockout.
- After lockout expires, user can retry with a fresh TOTP code.
- If `qrencode` is missing during enrollment, script exits non-zero and prints install guidance while still returning `otpauth_url` fallback.

## Sanity check

```bash
scripts/vault.sh put test/secret <<< "ok"
scripts/vault.sh exists test/secret
scripts/run_with_secret.sh --secret test/secret --env TEST_SECRET -- sh -c 'test "$TEST_SECRET" = "ok"'
scripts/vault.sh rm test/secret
```
