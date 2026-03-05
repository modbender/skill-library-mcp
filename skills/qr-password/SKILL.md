---
name: qr-password
description: Air-gapped credential bridge using QR codes. Use when transferring credentials between networked and air-gapped devices via QR codes. Triggers on: generating QR from credentials, reading QR codes containing credentials, air-gapped password transfer, credential QR codes, vault-to-QR, camera-to-credential.
---

# QR Password — Air-Gapped Credential Bridge

Bidirectional credential transfer using QR codes as an optical channel. No secret touches a network.

## Security Rules (MANDATORY)

- **Never log credentials to chat history or memory files**
- **Redact passwords from all conversation output** — show `****` instead
- **Auto-clear canvas display after 30 seconds** using timed canvas hide
- **QR images are ephemeral** — delete after use with `rm`
- **Never store decoded credentials in any file**

## Mode A: Vault → QR (Outbound)

Generate a QR code from a credential for an air-gapped device to scan.

```bash
echo '{"username":"USER","password":"PASS","domain":"DOMAIN"}' | \
  python3 skills/qr-password/scripts/generate-qr.py /tmp/qr-out.png
```

Then display via canvas and auto-clear:

```
canvas present /tmp/qr-out.png
# Wait 30s
canvas hide
rm /tmp/qr-out.png
```

When reporting to user, say "QR displayed" — never echo the password.

## Mode B: Camera → Credential (Inbound)

Read a QR code from a camera image to extract credentials.

1. Capture image: `nodes camera_snap` (or accept user-provided image)
2. Decode:

```bash
python3 skills/qr-password/scripts/read-qr.py /path/to/image.png
```

3. Output is JSON: `{"username":"...","password":"...","domain":"..."}`
4. Use the credential (fill, copy, deliver) — **never echo password to chat**
5. Delete the image: `rm /path/to/image.png`

## Offline QR Generator

For air-gapped devices, provide `assets/qr-generator.html` — a standalone offline HTML page that generates QR codes locally in-browser. No network required.

## Dependencies

Python 3 with: `qrcode`, `Pillow`, `opencv-python-headless`

Install: `python3 -m pip install --user qrcode Pillow opencv-python-headless`
