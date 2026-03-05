# Security Policy — FORTUNA Skill

## Why this skill requests SOLANA_PRIVATE_KEY

The optional fallback script scripts/send_sol.py uses a Solana private key **only** to sign transactions locally on your machine. This is needed to buy lottery tickets for agents that do not have an existing wallet integration (like Phantom MCP or solana-skills).

## What the private key is used for

- Signing a SOL transfer transaction to the hardcoded FORTUNA treasury address
- The treasury address is: BzHharnq5sa7TUWPSG1TysjwxuBVJchoU8CGRDmbLcfW
- This address matches the one published on https://fortunaonsol.com

## What the private key is NOT used for

- It is never sent to any external server
- It is never logged or stored to disk
- It is never included in any API call
- It is only read from the SOLANA_PRIVATE_KEY environment variable at runtime

## Recommendations

- If your agent already has Solana transfer capabilities, you do **not** need to set a private key. Just send SOL directly to the treasury address.
- If using the fallback script, create a **dedicated wallet with limited funds** specifically for lottery participation
- Never use your main wallet private key

## Audit

You can verify this by reading scripts/send_sol.py. It is a short, readable Python script (~90 lines) with no obfuscation, no network calls other than the Solana RPC, and no file writes.
