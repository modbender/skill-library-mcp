# LNbits Wallet Manager Skill for OpenClaw

Enable your OpenClaw assistant to safely and effectively manage an LNbits Lightning Network wallet.

## Features

- **Check Balance**: Get your current wallet balance in Satoshis.
- **Create Invoice**: Generate Bolt11 invoices to receive funds, with automatic QR code generation.
- **Pay Invoice**: Safely pay Bolt11 invoices after confirmation and balance checks.
- **Decode Invoice**: Inspect Bolt11 invoices to verify amount and memo.
- **Generate QR Code**: Create a QR code image from any Bolt11 invoice string.
- **Create Wallet**: Easily set up a new LNbits wallet on the demo server.

## 🛑 Critical Protocols for Safe Usage 🛑

To ensure secure and responsible handling of your LNbits wallet, this skill enforces strict protocols:

1.  **NEVER Expose Secrets**: The assistant is programmed to **NEVER** display Admin Keys, User IDs, or Wallet IDs in chat. Credentials are handled via environment variables.
2.  **Explicit Payment Confirmation**: The assistant **MUST** ask for "Yes/No" confirmation before sending any payment.
    *   **Confirmation Format**: "I am about to send **[Amount] sats** to **[Memo/Destination]**. Proceed? (y/n)"
3.  **Balance Check Before Pay**: The assistant will always check your wallet balance before attempting to pay an invoice to prevent failed transactions.
4.  **Invoice + QR Output**: When generating an invoice, the assistant will **ALWAYS** provide:
    *   The `payment_request` text string for easy copying.
    *   An `IMAGE:` link to the generated QR code file on a single line, allowing direct display of the QR code.

## Installation

This skill requires the `qrcode[pil]` Python library.

1.  **Install ClawHub CLI**:
    ```bash
    npm i -g clawhub
    ```
2.  **Install the Skill**:
    ```bash
    clawhub install lnbits
    ```

## Configuration

The skill uses environment variables for LNbits API credentials. It's recommended to add these to your OpenClaw configuration or your agent's `.env` file.

-   `LNBITS_BASE_URL`: The base URL of your LNbits instance (e.g., `https://legend.lnbits.com` or your self-hosted URL).
-   `LNBITS_API_KEY`: Your LNbits wallet's Admin Key.

Example `.env` entries:
```dotenv
export LNBITS_BASE_URL=https://legend.lnbits.com
export LNBITS_API_KEY=YOUR_ADMIN_KEY_HERE
```

## Usage Examples

Here's how you can use the `lnbits` skill with your OpenClaw assistant:

### 0. Setup / Create Wallet

If you don't have an LNbits wallet, you can create one (defaults to the demo server for ease of setup):

```
(User): Create a new lnbits wallet named "My OpenClaw Wallet"
```
The create command prints your new `adminkey` and `base_url` in the terminal output. Copy those from the command output and save them securely in your environment variables (e.g. `.env`). The assistant will not repeat or display the adminkey in chat.

### 1. Check Balance

Ask your assistant for the current balance:

```
(User): What's my lnbits balance?
```

### 2. Create Invoice (Receive Funds)

Generate an invoice for receiving funds:

```
(User): Create an invoice for 5000 sats for "Coffee"
```

The assistant will provide the Bolt11 invoice string and a QR code image.

### 2b. Generate QR Code from Existing Invoice

If you have a Bolt11 string and need a QR code:

```
(User): Generate a QR code for this invoice: lnbc1u1p...
```

### 3. Pay Invoice (Send Funds)

To pay an invoice, the assistant will first decode it and then ask for confirmation:

```
(User): Pay this invoice: lnbc1u1p...
```
The assistant will then prompt: "I am about to send **[Amount] sats** to **[Memo/Dest]**. Proceed? (y/n)"

## Error Handling

The skill is designed to catch and summarize API errors from LNbits, providing clear feedback to the user without exposing raw technical details or stack traces.

---

**Developed for OpenClaw - The AI Orchestration Layer**
