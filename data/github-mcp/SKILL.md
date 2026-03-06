---
name: github-mcp
description: GitHub MCP Server for repository management, file operations, PR/issue tracking, branch management, and GitHub API integration. Enable AI agents to clone repos, read code, create/update files, manage issues and pull requests, search code, and interact with the GitHub platform. Essential for development workflows, code review automation, CI/CD management, and repository operations. Use when agents need to work with Git repositories, manage development workflows, automate GitHub tasks, or interact with source code.
---

# GitHub MCP Server

> **Complete GitHub Integration for AI Agents**

Connect AI agents to GitHub for repository management, code operations, issue tracking, pull requests, and the full GitHub API.

## Why GitHub MCP?

### 🤖 Agent-Native GitHub Workflows
Enable agents to perform complex GitHub operations that previously required manual API integration:
- Clone and navigate repositories
- Read and modify files
- Create issues and pull requests
- Review code and discussions
- Manage branches and releases

### 🔐 Secure Authentication
OAuth-based authentication with fine-grained permissions. Agents access only what you authorize.

### 📦 Zero Setup for Common Operations
Pre-configured tools for the most common GitHub workflows. No manual API calls required.

## Installation

### Option 1: Official MCP Server (Archived - Community Maintained)

```bash
# Community-maintained GitHub MCP server
npm install -g @modelcontextprotocol/server-github

# Or build from source
git clone https://github.com/modelcontextprotocol/servers-archived
cd servers-archived/src/github
npm install
npm run build
```

### Option 2: Third-Party Implementations

Several community implementations available. Check the [MCP Registry](https://registry.modelcontextprotocol.io/) for current options.

## Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

### Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Generate new token (classic) or fine-grained token
3. Select scopes:
   - `repo` - Full repository access
   - `read:user` - Read user profile
   - `read:org` - Read organization data (if needed)

**Fine-Grained Token** (recommended):
- Repository permissions: Contents (Read/Write), Issues (Read/Write), Pull Requests (Read/Write)
- Organization permissions: Members (Read) if accessing org repos

## Available Tools

### Repository Operations

#### 1. **Create Repository**
```
Agent: "Create a new repository called 'my-project'"
```

#### 2. **Clone Repository**
```
Agent: "Clone the OpenAI GPT-4 repository"
```

#### 3. **List Repository Files**
```
Agent: "What files are in the src/ directory?"
```

### File Operations

#### 4. **Read File**
```
Agent: "Show me the README.md file"
Agent: "Read the contents of src/index.ts"
```

#### 5. **Create/Update File**
```
Agent: "Create a new file docs/API.md with API documentation"
Agent: "Update the version in package.json to 2.0.0"
```

#### 6. **Search Code**
```
Agent: "Search for files containing 'authentication logic'"
Agent: "Find where the DatabaseConnection class is defined"
```

### Issue & PR Management

#### 7. **Create Issue**
```
Agent: "Create an issue: 'Add dark mode support'"
```

#### 8. **List Issues**
```
Agent: "Show me all open bugs"
Agent: "What issues are assigned to me?"
```

#### 9. **Create Pull Request**
```
Agent: "Create a PR to merge feature/login into main"
```

#### 10. **Review Pull Request**
```
Agent: "Review PR #42 and check for security issues"
```

### Branch Operations

#### 11. **Create Branch**
```
Agent: "Create a new branch called 'feature/user-auth'"
```

#### 12. **List Branches**
```
Agent: "Show all branches in this repo"
```

#### 13. **Merge Branch**
```
Agent: "Merge 'develop' into 'main'"
```

### Advanced Operations

#### 14. **Create Release**
```
Agent: "Create a release v2.0.0 with the latest changes"
```

#### 15. **Search Repositories**
```
Agent: "Find popular React component libraries"
```

#### 16. **Fork Repository**
```
Agent: "Fork the Vue.js repository to my account"
```

## Agent Workflow Examples

### Code Review Automation

```
Human: "Review all PRs and flag security issues"

Agent:
1. list_pull_requests(state="open")
2. For each PR:
   - get_pull_request(pr_number)
   - read_changed_files()
   - analyze for security vulnerabilities
   - create_review_comment(security_findings)
```

### Issue Triage

```
Human: "Label all new issues with 'needs-triage'"

Agent:
1. list_issues(state="open", labels=null)
2. For each unlabeled issue:
   - read_issue(issue_number)
   - add_label("needs-triage")
```

### Release Automation

```
Human: "Prepare v2.0.0 release"

Agent:
1. create_branch("release/v2.0.0")
2. update_file("package.json", version="2.0.0")
3. update_file("CHANGELOG.md", new_release_notes)
4. create_pull_request("release/v2.0.0" -> "main")
5. create_release(tag="v2.0.0", notes=changelog)
```

### Documentation Sync

```
Human: "Update documentation from code comments"

Agent:
1. search_code(query="* @description")
2. extract_docstrings()
3. generate_markdown_docs()
4. update_file("docs/API.md", generated_docs)
5. create_pull_request("Update API documentation")
```

## Use Cases

### 🛠️ Development Assistants
Agents that help developers with repetitive GitHub tasks: creating issues, managing labels, updating documentation, code review.

### 🤖 CI/CD Automation
Build agents that trigger workflows, check build status, create releases, manage deployments.

### 📊 Repository Analytics
Analyze code quality, track issue resolution time, monitor PR velocity, generate reports.

### 🔍 Code Search & Discovery
Find code patterns, identify dependencies, discover similar implementations, locate technical debt.

### 📝 Documentation Automation
Sync code comments to docs, generate API references, update changelogs, maintain README files.

## Security Best Practices

### ✅ Use Fine-Grained Tokens
Prefer fine-grained tokens over classic PATs. Limit scope to specific repositories and permissions.

### ✅ Read-Only When Possible
If the agent only needs to read code/issues, grant read-only access.

### ✅ Environment Variables
Never hard-code tokens. Always use environment variables.

### ✅ Token Rotation
Rotate tokens regularly. Set expiration dates.

### ✅ Audit Agent Actions
Monitor what the agent does. GitHub activity log tracks all API operations.

## Rate Limits

**Authenticated Requests:**
- 5,000 requests/hour (per user)
- Search API: 30 requests/minute

**Best Practices:**
- Cache repository data when possible
- Batch operations where applicable
- Use conditional requests (`If-None-Match` headers)

## vs Manual GitHub API Integration

| Task | Manual API | GitHub MCP |
|------|------------|-----------|
| **Setup Time** | Hours (auth, SDK, error handling) | Minutes (config file) |
| **Code Required** | Yes (HTTP client, auth, parsing) | No (MCP tools auto-discovered) |
| **Agent Integration** | Manual tool definitions | Automatic via MCP |
| **Auth Management** | Custom implementation | Built-in OAuth flow |
| **Error Handling** | Custom retry logic | Handled by server |

## Troubleshooting

### "Bad credentials" Error
- Verify token has not expired
- Ensure token has required scopes (`repo`, `read:user`)
- Check token is correctly set in environment variable

### "Resource not found" Error
- Verify repository name format: `owner/repo`
- Check agent has access to private repositories (if applicable)
- Ensure branch/file path exists

### Rate Limit Errors
- Wait for rate limit reset (check `X-RateLimit-Reset` header)
- Reduce query frequency
- Consider GitHub Apps for higher limits

## Resources

- **MCP Registry**: https://registry.modelcontextprotocol.io/
- **GitHub API Docs**: https://docs.github.com/en/rest
- **Create Token**: https://github.com/settings/tokens
- **Rate Limits**: https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api

## Advanced Configuration

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/path/to/github-mcp/build/index.js"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx",
        "GITHUB_API_URL": "https://api.github.com",
        "DEFAULT_BRANCH": "main",
        "AUTO_PAGINATION": "true"
      }
    }
  }
}
```

---

**The GitHub integration every coding agent needs**: From code review to release automation, GitHub MCP brings the full power of GitHub to AI agents.
