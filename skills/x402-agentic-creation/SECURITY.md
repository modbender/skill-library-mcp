# Security and trust boundaries

This document describes how the x402-creation skill handles credentials and external communication so that auditors and operators can reason about risk and whitelisting.

## Backend communication

- **Single backend**: This skill communicates **only** with `https://api.gatex402.dev`. No other domains are used.
- **Purpose**: The protocol requires this backend for provisioning, balance, and withdrawals (nonce, signing, payout). Data sent includes wallet address, signatures, nonces, and transaction metadata as required by the x402 protocol.
- **Whitelisting**: For environments that maintain a trusted-domain whitelist (e.g. Gen Agent Trust Hub), we request that `api.gatex402.dev` (and optionally `gatex402.dev` for documentation links) be whitelisted as the intended backend for this skill.

## Credentials

- **Wallet private key**: Never exposed to the agent or in tool parameters. Supplied only by the host via `createTools({ getWalletPrivateKey })` (e.g. from env or a secure vault).
- **Management token**: Never returned to the agent. The `provision_api` tool **never includes `management_token` in its return value**; the tool response contains only `api_slug`, `provider_id`, and a non-sensitive message. After provisioning, the token is passed to the host via `storeManagementToken` and later supplied to the tools via `getManagementToken`.

## Response handling (indirect prompt injection)

- All responses from `api.gatex402.dev` are **sanitized**: only a minimal, typed subset of fields (e.g. numeric balances, status, `tx_hash`) is returned to the agent.
- Sanitized responses are wrapped in boundary markers: `<!-- GATEX402_API_RESPONSE --> ... <!-- END_GATEX402_API_RESPONSE -->` so downstream logic can treat them as skill output.

## Installation

- **Preferred**: Install from npm (`npm install x402-creation`) and add the skill from the official repo or package path. This avoids executing code from unverified third-party registries.
- **Alternative**: If you use a third-party registry (e.g. `npx skills add ...`), ensure that registry is trusted or whitelisted in your environment.
