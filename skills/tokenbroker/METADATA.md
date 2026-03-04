# METADATA.md - Token Asset Generation

**version: 1.01**

---

## Required Environment Variables

```yaml
requiredEnvironmentVariables:
  - name: GITHUB_TOKEN
    description: GitHub Personal Access Token for repository scanning (stored locally in .env)
    optional: false
  - name: PRIVATE_KEY
    description: EVM private key for wallet operations (stored locally, never exposed externally)
    optional: false
  - name: BUILDER_ID
    description: Unique builder identifier for A2A protocol (stored locally)
    optional: false
  - name: NETWORK
    description: Network to deploy to (mainnet or testnet)
    optional: false
    default: testnet
  - name: NAD_FUN_API_KEY
    description: API key for nad.fun token creation (stored locally in .env)
    optional: true
```

## Security Notes

```yaml
securityNotes:
  - All secrets stored locally in .env file
  - No external data transmission of credentials
  - Supports testnet mode for safe testing
  - Uses standard EVM wallet signing
```

---

**Turn raw project data into a compelling token identity.**

This module guides the agent in generating creative and compliant metadata for the nad.fun token launch.

> **Key Point:** TokenBroker generates metadata proposals. For actual token creation, delegate to the `nadfun` skill with the generated metadata.

This module guides the agent in generating creative and compliant metadata for the nad.fun token launch.

> **Key Point:** TokenBroker generates metadata proposals. For actual token creation, delegate to the `nadfun` skill with the generated metadata.

## 1. Naming Strategy

When helping a user pick a token name/symbol, use these strategies:

### A. The Ecosystem Token
Directly named after the project. Best for serious utilities.
*   **Source**: "OpenClaw"
*   **Name**: "OpenClaw Token"
*   **Symbol**: `$CLAW`

### B. The Mascot/Meme
A character or concept derived from the project's brand. High engagement potential.
*   **Source**: "TokenBroker" (Lobster emoji used in docs)
*   **Name**: "Broker Lobster"
*   **Symbol**: `$LOBSTER`

### C. The DAO/Governance
For community-led initiatives.
*   **Source**: "Builder Toolkit"
*   **Name**: "Builder DAO"
*   **Symbol**: `$BUILD`

## 2. Description Generation

Descriptions on nad.fun should be punchy (under 280 chars recommended) but informative.

**Template:**
> "The official [Utility/Meme] token for [Project Name]. [Value Prop]. Powered by [Tech Stack] on Monad."

**Example:**
> "The official automation token for TokenBroker. Deploy agents instantly and mine launches on nad.fun. Powered by OpenClaw on Monad. 🦞"

## 3. Metadata Structure

The nad.fun API expects this exact JSON structure:

```json
{
  "name": "My Token",
  "symbol": "MTK",
  "description": "Token description",
  "image_uri": "ipfs://...",
  "website": "https://...", 
  "twitter": "https://x.com/...",
  "telegram": "https://t.me/..."
}
```

## 4. Delegating to nadfun

Once metadata is approved by the user, delegate token creation to the `nadfun` skill:

```typescript
async function createTokenWithNadfun(metadata: TokenMetadata) {
  const result = await invokeSkill("nadfun", {
    action: "create",
    name: metadata.name,
    symbol: metadata.symbol,
    description: metadata.description,
    imageUri: metadata.image_uri,
    metadataUri: metadata.metadata_uri,
    website: metadata.website,
    twitter: metadata.twitter,
    telegram: metadata.telegram
  });
  
  return result;
}
```

### Metadata Output Schema

When presenting metadata proposals to users:

```json
{
  "proposals": [
    {
      "id": 1,
      "strategy": "ecosystem",
      "name": "Project Token",
      "symbol": "$PROJ",
      "description": "The official utility token for Project Name..."
    }
  ],
  "readyForNadfun": {
    "name": "Project Token",
    "symbol": "PROJ",
    "description": "...",
    "image_uri": "ipfs://...",
    "metadata_uri": "ipfs://..."
  }
}
```

## 5. Agent Prompts

**Prompt:** "Suggest 3 token ideas for this project."
**Agent Action:**
1.  Read `PROJECT-SCAN.md` output.
2.  Apply Strategies A, B, and C.
3.  Output a table with Name, Symbol, and Description for each.
4.  Present with clear delegation option: "Ready to launch? Invoke nadfun with approved metadata."

## Next Steps

Once metadata is approved by the user:
- Go to **LAUNCH.md** for orchestration instructions
- Delegate to `nadfun` skill for actual on-chain creation
