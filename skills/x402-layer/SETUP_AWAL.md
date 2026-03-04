# Setup Guide: Coinbase Agentic Wallet (AWAL) CLI

To use the `x402-layer` skill with Coinbase Agentic Wallet (AWAL) for Base payments, you need to install the `awal` CLI tool.

## Prerequisites

- Node.js (version 18+ recommended)
- NPM or Yarn

## Option 1: Global Installation (Recommended)

Installing globally allows you to run `awal` commands directly from any directory.

```bash
npm install -g awal
```

Verify installation:
```bash
awal --version
```

## Option 2: Using NPX (No Installation Required)

You can run commands without installing `awal` globally by prefixing with `npx`.

```bash
npx awal --version
```

## Authentication

1.  **Login**: Start the authentication process. You will receive an email with an OTP.
    ```bash
    # If installed globally:
    awal auth login your-email@example.com

    # If using npx:
    npx awal auth login your-email@example.com
    ```

2.  **Verify**: Check your email for the OTP and complete the login.
    ```bash
    # Replace <flow-id> and <otp-code> with values from the login step and email.
    awal auth verify <flow-id> <otp-code>
    ```

3.  **Check Status**: Confirm you are logged in.
    ```bash
    awal status
    ```

## Configuration for x402-layer

Once setup, ensure you export the necessary environment variable to enable AWAL mode in the scripts:

```bash
export X402_USE_AWAL=1
```
