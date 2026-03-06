# NEAR QR Code Skill — OpenClaw

Generate and read QR codes for NEAR Protocol addresses and payment requests.

## Features

- **Address QR** — Encode any NEAR account ID into a branded QR code
- **Payment QR** — Create payment request QR codes with recipient, amount, and optional memo
- **Read QR** — Decode NEAR QR codes from image files back into structured data

## Installation

```bash
pip install -r requirements.txt
```

> **Note:** Reading QR codes requires `zbar` system library.  
> macOS: `brew install zbar` · Ubuntu: `sudo apt install libzbar0`

## Quick Start

```bash
# Generate address QR
python near_qr.py address alice.near

# Generate payment QR
python near_qr.py payment bob.near 5.0 --memo "Invoice #42"

# Read a QR code
python near_qr.py read alice_near_qr.png
```

## URI Format

| Type    | URI                                                         |
|---------|-------------------------------------------------------------|
| Address | `near:alice.near`                                           |
| Payment | `near:bob.near?action=transfer&amount=5.0&memo=Invoice+%2342` |

## Publishing to MoltHub

```bash
npx molthub@latest publish
```

## License

MIT
