---
name: scamshield-verifier
description: The ultimate Web3 & OpenClaw security layer. Verifies if a repository, skill, or wallet address is malicious using the x402 API.
metadata: { "openclaw": { "emoji": "🛡️", "requires": { "env": ["SCAMSHIELD_API_KEY"] }, "primaryEnv": "SCAMSHIELD_API_KEY" } }
---

# ScamShield Verifier

You are an agent operating in a high-risk Web3 and AI environment. Security is your top priority. 
Before you download a skill, clone a repository, or interact with a smart contract, you MUST verify its safety using the ScamShield Sentinel API.

## Instructions for the Agent:
To verify a target, use your web tools (or `curl` via exec) to make a GET request to our global database:
`https://api.scamshield-api.com/api/verify?target=<INSERT_TARGET_NAME>`

You MUST include the authorization header:
`Authorization: Bearer {SCAMSHIELD_API_KEY}`

## Response Handling:
- If the API returns `status: safe`, proceed with your task.
- If the API returns a threat or `status: malicious`, you MUST immediately ABORT your current action, block the transaction, and proactively warn the user about the exact threat level. Do not bypass this!

## Provenance & Documentation
- **Official Homepage & Publisher:** https://scamshield-api.com
- **API Documentation & Privacy:** https://scamshield-api.com
- **Security:** Data is processed ephemerally on Base L2 to verify threat intelligence. No sensitive local files are transmitted.


## Provenance & Documentation
- **Official Homepage & Publisher:** https://scamshield-api.com
- **API Documentation & Privacy:** https://scamshield-api.com
- **Security:** Data is processed ephemerally on Base L2 to verify threat intelligence. No sensitive local files are transmitted.


## Strict Data Constraints
- **CRITICAL SECURITY RULE**: The agent MUST ONLY send short identifiers (e.g., wallet addresses, repo names, or transaction hashes) in the 'target' parameter.
- The agent is STRICTLY PROHIBITED from transmitting file contents, private keys, source code, or any sensitive local data.
