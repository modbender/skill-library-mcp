# LAUNCH.md - Token Launch Orchestration

**Guide for delegating token launches to the nadfun skill.**

TokenBroker handles project analysis and metadata generation, then delegates actual on-chain operations to the `nadfun` skill. This document explains the orchestration flow.

> **Security Note**: TokenBroker is a meta-skill that orchestrates operations. All wallet credentials and sensitive operations are handled by the `nadfun` skill with its own security protocols. Credentials are injected by the host environment at runtime.

## Orchestration Flow

### Step 1: Analysis Complete (TokenBroker)
Before launching, ensure you've:
- Scanned the project (`PROJECT-SCAN.md`)
- Generated metadata proposals (`METADATA.md`)
- Obtained user approval for token details

### Step 2: Delegate to nadfun (On-Chain Operations)

For actual token creation, invoke the `nadfun` skill. TokenBroker passes the prepared metadata to nadfun for on-chain execution.

```typescript
// Example: Delegating token creation to nadfun skill
const launchRequest = {
  tokenName: "Project Name",
  tokenSymbol: "SYMBOL",
  description: "Token description...",
  imageUri: "ipfs://...", // From metadata generation
  metadataUri: "ipfs://...", // From metadata generation
  salt: "0x...", // Optional: nadfun will mine if not provided
  initialBuy: "0", // Optional MON amount for initial buy
};

// Delegate to nadfun skill for execution
const result = await invokeSkill("nadfun", {
  action: "create",
  ...launchRequest
});
```

## What nadfun Handles

The `nadfun` skill executes the following operations:

1. **Image Upload**: Uploads token image to IPFS via nad.fun API
2. **Metadata Upload**: Creates and uploads metadata JSON to IPFS
3. **Salt Mining**: Generates vanity address ending in "7777"
4. **Contract Deployment**: Calls `BondingCurveRouter.create()` on-chain
5. **Transaction Confirmation**: Returns the deployed token address

## Delegation Examples

### Complete Launch Orchestration

```typescript
async function orchestrateTokenLaunch(projectData: ProjectScanResult) {
  // Step 1: Generate metadata (TokenBroker)
  const metadata = await generateTokenMetadata(projectData);
  
  // Step 2: Present to user for approval
  const userApproval = await presentLaunchProposal(metadata);
  if (!userApproval.approved) {
    return { success: false, reason: "User rejected launch" };
  }
  
  // Step 3: Delegate to nadfun for on-chain creation
  const launchResult = await invokeSkill("nadfun", {
    action: "create",
    name: metadata.name,
    symbol: metadata.symbol,
    description: metadata.description,
    imageUri: metadata.imageUri,
    metadataUri: metadata.metadataUri,
    website: metadata.socials?.website,
    twitter: metadata.socials?.twitter,
    telegram: metadata.socials?.telegram
  });
  
  if (launchResult.success) {
    // Step 4: Update builder stats
    await updateBuilderStats(launchResult.tokenAddress);
  }
  
  return launchResult;
}
```

### Passing GitHub Context to nadfun

```typescript
// When launching from GitHub monitoring context
const contextLaunch = await invokeSkill("nadfun", {
  action: "create",
  name: githubContext.projectName,
  symbol: githubContext.projectSymbol,
  description: githubContext.description,
  // GitHub-specific metadata for verification
  extensions: {
    github_repo: githubContext.repoUrl,
    github_stars: githubContext.stars,
    launch_trigger: githubContext.triggerEvent
  }
});
```

## Post-Launch (TokenBroker)

After nadfun completes the launch:

1. **Verify**: Check the returned token address
2. **Promote**: Use `PROMO.md` to generate marketing content
3. **Track**: Update `STATS.md` with new launch

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Metadata mismatch | Ensure name/symbol match exactly what was proposed |
| Image rejected | Upload a new image via nadfun's image endpoint |
| Salt collision | nadfun will retry with new salt automatically |
| Insufficient funds | User needs at least 10 MON for deployment |

## Security Considerations

TokenBroker delegates all sensitive operations to the `nadfun` skill:

- **Wallet Management**: Handled by `nadfun` with secure credential injection
- **Private Keys**: Never processed by TokenBroker - injected via `${PRIVATE_KEY}` environment variable
- **Transaction Signing**: Occurs within the `nadfun` skill's secure context
- **Token Creation**: All on-chain operations execute within dependency skills

For detailed security practices, see the [Security Best Practices section in SKILL.md](./SKILL.md#security-best-practices).

---

*For direct API documentation, see [nad.fun/llms.txt](https://nad.fun/llms.txt)*
