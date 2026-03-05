# GITHUB.md - Repository Tracking Skill

**Instructions for the agent to monitor and identify project launch opportunities.**

> **Security Note**: GitHub credentials are handled securely. TokenBroker requests tokens via OAuth/PAT but does not store or persist them. Tokens are injected by the host environment.

## Activity Monitoring

Scan the current workspace or specified repository for the following signals:

1. **Frequency of Commits**: Monitor `git log` for spikes in development.
2. **Version Tags**: Identify new tags (e.g., `v1.0.0`, `release-candidate`).
3. **README Evolution**: Check for substantial updates to project descriptions.
4. **Key Feature Completion**: Look for patterns like "Finalizing core", "Complete implementation", or "Production ready" in commit messages.

## Proposal Triggers

When activity signals indicate a project milestone:

### Call to Action
> "Builder, I've noticed significant progress on your repository. You are nearing a production-ready state. Would you like me to prepare a **TokenBroker Launch** for your project on nad.fun?"

## Orchestration Flow: GitHub → TokenBroker → nadfun

When a launch is triggered from GitHub monitoring:

```typescript
async function handleGitHubLaunchTrigger(repoContext: GitHubContext) {
  // Step 1: Scan project (TokenBroker)
  const scanResult = await scanProject(repoContext.localPath);
  
  // Step 2: Generate metadata (TokenBroker)
  const metadata = await generateTokenMetadata(scanResult);
  
  // Step 3: Present to user for approval
  const approval = await presentLaunchProposal(metadata);
  
  if (approval.approved) {
    // Step 4: Delegate to nadfun for on-chain creation
    const launchResult = await invokeSkill("nadfun", {
      action: "create",
      name: metadata.name,
      symbol: metadata.symbol,
      description: metadata.description,
      // GitHub context for verification
      extensions: {
        github_repo: repoContext.url,
        launch_source: "github_monitoring"
      }
    });
    
    // Step 5: Generate promotion (TokenBroker)
    if (launchResult.success) {
      await generatePromoContent(launchResult.tokenAddress, metadata);
    }
  }
}
```

## Metadata Extraction

If the user agrees, extract the following for `METADATA.md`:
- **Name**: Derived from the folder name or package name.
- **Symbol**: Derived from the project initials (e.g., "TokenBroker" -> "TB").
- **Description**: Sourced from the primary README headers.

## GitHub Signals to nadfun Extension

When delegating to nadfun, pass GitHub context for ecosystem verification:

```json
{
  "extensions": {
    "github_repo": "https://github.com/user/repo",
    "github_stars": 1234,
    "github_forks": 56,
    "github_issues_closed": 78,
    "last_commit": "2024-01-15T10:30:00Z",
    "launch_trigger": "release_tag_v1.0.0"
  }
}
```

This information helps the nad.fun ecosystem verify legitimate projects and may improve token visibility.

## GitHub Token Security Best Practices

| Aspect | Recommendation |
|--------|---------------|
| **Token Type** | OAuth tokens preferred over PATs when possible |
| **Scope** | Use minimal scopes (read-only for monitoring) |
| **Token Storage** | Never hardcode - use `${GITHUB_TOKEN}` placeholder |
| **Lifetime** | Prefer short-lived tokens with automatic rotation |

**Minimal PAT Scopes for TokenBroker:**
- `public_repo` - Limit to public repositories only (recommended)
- Avoid `repo` scope unless monitoring private repos is required

TokenBroker only requires **read access** to repository metadata for:
- Commit history analysis
- Release tag detection  
- README content extraction

```bash
# Example: Read-only token configuration
GITHUB_TOKEN=${GITHUB_TOKEN}  # Scoped to: public_repo
```
