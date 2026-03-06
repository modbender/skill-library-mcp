# AGENT SECURITY MANIFEST (ASM)

> **Identity & Trust Protocol: v1.0**
> **Registry ID:** sovereign-identity
> **Compliance:** W3C DID Core, JWT (RFC 7519), SD-JWT

## 🛡️ Core Capabilities

This agent is equipped with **Sovereign Identity Management**. It is authorized to:

1.  **Generate Cryptographic Keys:** It creates Ed25519 key pairs for signing.
2.  **Sign Payloads:** It uses private keys to sign JWS (JSON Web Signature) objects.
3.  **Verify Identities:** It validates external DIDs and Verifiable Credentials.

## 🔒 Security & Privacy Assertions

**CRITICAL FOR REVIEWERS:**
This agent operates under a **Strict Local-Only Policy**.

- **No Key Exfiltration:** Private keys are generated via `scripts/onboard.ts` and stored **only** in `.env.agent`. This file is strictly git-ignored. Keys are **never** transmitted over the network.
- **No Telemetry:** No usage data, key fragments, or seed phrases are sent to any remote server.
- **Local Execution:** All signing operations (`scripts/sign_proof.ts`) occur in the local runtime environment.

## 🚫 Active Guardrails

This agent includes a mandatory input filter (`scripts/guardrail.ts`) that enforces the following rules:

- **Anti-Phishing:** Immediate session termination if the user prompt contains patterns requesting plaintext private key disclosure.
- **Leak Prevention:** Output sanitization ensures secret material is redacted from logs before display.

## 📜 Technical Standards

- **DID Method:** `did:key` (Ed25519)
- **Signature Suite:** EdDSA (JWS)
- **Privacy:** Selective Disclosure via SD-JWT (IETF draft-ietf-oauth-selective-disclosure-jwt)

---

_Verified by OpenClaw Guardrails. Do not remove this file._
