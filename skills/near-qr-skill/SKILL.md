---
name: near-qr-code
description: Generate QR codes for NEAR addresses and payment requests, and read NEAR QR codes from images.
version: 1.0.0
author: humanAgent
tags:
  - near
  - qr-code
  - payments
  - blockchain
---

# NEAR QR Code Skill

Generate and read QR codes for NEAR Protocol addresses and payment requests.

## Setup

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Commands

### 1. Generate Address QR — `near_qr_address`

Generate a QR code containing a NEAR account address.

**Usage:**
```bash
python near_qr.py address <account_id> [--output <path>] [--size <pixels>]
```

**Parameters:**
- `account_id` (required) — The NEAR account address (e.g. `alice.near`)
- `--output` — Output file path (default: `<account_id>_qr.png`)
- `--size` — QR image size in pixels (default: `400`)

**Example:**
```bash
python near_qr.py address alice.near --output alice_qr.png --size 500
```

---

### 2. Generate Payment QR — `near_qr_payment`

Generate a QR code for a NEAR payment request, encoding recipient, amount, and optional memo.

**Usage:**
```bash
python near_qr.py payment <to> <amount> [--memo <text>] [--output <path>] [--size <pixels>]
```

**Parameters:**
- `to` (required) — Recipient NEAR account (e.g. `bob.near`)
- `amount` (required) — Amount of NEAR to request (e.g. `2.5`)
- `--memo` — Optional memo or reference note
- `--output` — Output file path (default: `payment_qr.png`)
- `--size` — QR image size in pixels (default: `400`)

**Example:**
```bash
python near_qr.py payment bob.near 5.0 --memo "Invoice #42" --output pay_bob.png
```

---

### 3. Read QR Code — `near_qr_read`

Decode a NEAR QR code from an image file and extract the embedded data.

**Usage:**
```bash
python near_qr.py read <image_path>
```

**Parameters:**
- `image_path` (required) — Path to the QR code image

**Example:**
```bash
python near_qr.py read alice_qr.png
```

**Output:** Returns a JSON object with the decoded type and data:
```json
{
  "type": "near_address",
  "account": "alice.near"
}
```
or for payment QR codes:
```json
{
  "type": "near_payment",
  "to": "bob.near",
  "amount": "5.0",
  "memo": "Invoice #42"
}
```
