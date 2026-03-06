# Meegle MCP Skill for OpenClaw

📊 Integrate Meegle project management with OpenClaw using the Model Context Protocol.

## Overview

This skill enables OpenClaw to interact with [Meegle](https://www.meegle.com/), a visual workflow and project management tool powered by Larksuite. Manage projects, tasks, workflows, and team collaboration directly through natural language commands.

## Features

- ✅ Project management (create, list, update)
- ✅ Task operations (create, assign, track, update)
- ✅ Workflow automation
- ✅ Team collaboration and permissions
- ✅ Time tracking and analytics
- ✅ Real-time synchronization with Meegle workspace

## Prerequisites

- OpenClaw installed ([Installation Guide](https://docs.openclaw.ai/installation))
- Node.js 16+ ([Download](https://nodejs.org/))
- Meegle account with API access
- Your Meegle User Key

## Quick Start

### 1. Install the Skill

**Option A: Via ClawHub (Recommended)**

```bash
clawhub install meegle-mcp
```

**Option B: From GitHub**

```bash
git clone <this-repo> meegle-mcp
cd meegle-mcp
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

The setup script will:
- Check Node.js installation
- Prompt for your Meegle User Key and MCP Key
- Configure credentials (environment variable or config file)
- Make necessary scripts executable

### 3. Restart OpenClaw

```bash
openclaw restart
```

### 4. Verify Installation

```bash
openclaw skills list | grep meegle
```

## Manual Installation

If you prefer manual setup:

### Option A: Environment Variable (Recommended)

1. Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):
   ```bash
   export MEEGLE_USER_KEY="your_user_key_here"
   export MEEGLE_MCP_KEY="your_mcp_key_here"
   ```

2. Reload your shell:
   ```bash
   source ~/.zshrc
   ```

   **Note**: Both `MEEGLE_USER_KEY` and `MEEGLE_MCP_KEY` are required. You can obtain these from your Meegle workspace administrator.

### Option B: Config File

1. Create or edit your OpenClaw MCP servers config file with:
   ```json
   {
     "mcpServers": {
       "meegle": {
         "command": "node",
         "args": ["<skill-directory>/scripts/mcp-proxy.js"],
         "env": {
           "MEEGLE_USER_KEY": "your_user_key_here",
           "MEEGLE_MCP_URL": "https://project.larksuite.com/mcp_server/v1",
           "MEEGLE_MCP_KEY": "your_mcp_key_here"
         },
         "status": "active"
       }
     }
   }
   ```

   Replace `<skill-directory>` with the actual path where the skill is installed.

2. Make the proxy script executable:
   ```bash
   chmod +x scripts/mcp-proxy.js
   ```

## Usage Examples

Once installed, use natural language to interact with Meegle:

```bash
# List projects
openclaw ask "Show me all my Meegle projects"

# Create a task
openclaw ask "Create a task in Meegle: Update documentation, due Friday, assign to @john"

# Check task status
openclaw ask "What high-priority tasks are pending in Meegle?"

# Update workflow
openclaw ask "Move task 'Homepage design' to In Review stage in Meegle"

# Team management
openclaw ask "Add sarah@company.com to the Mobile App project in Meegle"

# Analytics
openclaw ask "Show me project completion stats for this month in Meegle"
```

## Finding Your Keys

You need two keys to use this skill:

### MEEGLE_USER_KEY
Your Meegle User Key is provided by your workspace administrator. To locate it:

1. Log in to your Meegle workspace
2. Navigate to **Settings** → **API Access**
3. Copy your User Key
4. Keep it secure (treat it like a password)

### MEEGLE_MCP_KEY
Your Meegle MCP Key is also provided by your workspace administrator. This key is required for MCP protocol authentication:

1. Contact your workspace administrator
2. Request your MCP Key for API integration
3. Store it securely alongside your User Key

**Security Note**: Never share these keys publicly or commit them to version control.

## Troubleshooting

### Authentication Errors

```bash
# Verify your keys are set
echo $MEEGLE_USER_KEY
echo $MEEGLE_MCP_KEY

# Check OpenClaw logs
openclaw logs --filter=meegle
```

### MCP Server Not Responding

1. Check network connectivity to `project.larksuite.com`
2. Verify both your User Key and MCP Key haven't expired
3. Ensure both environment variables are properly set
4. Ensure Node.js is properly installed: `node --version`

### Skills Not Loading

```bash
# Restart OpenClaw
openclaw restart

# Check skill status
openclaw skills list --verbose
```

## Publishing to ClawHub

Want to share this skill with the community? Here's how to publish to [ClawHub](https://clawhub.ai/):

### 1. Prepare Repository

Ensure your repository has:
- ✅ `SKILL.md` (with proper frontmatter)
- ✅ `README.md` (this file)
- ✅ `LICENSE` (choose an open-source license)
- ✅ Scripts in `scripts/` directory
- ✅ Example config in `mcp-config.example.json`

### 2. Create GitHub Repository

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: Meegle MCP skill"

# Create repo on GitHub, then push
git remote add origin https://github.com/pkycy/meegle-mcp-skill.git
git branch -M main
git push -u origin main
```

### 3. Publish to ClawHub

#### Via CLI (Recommended)

```bash
# Install ClawHub CLI if not already installed
npm install -g clawhub-cli

# Login
clawhub login

# Publish
clawhub publish
```

#### Via Web Interface

1. Visit [ClawHub](https://clawhub.ai/)
2. Sign in with GitHub
3. Click **Publish Skill**
4. Enter your repository URL
5. Fill in metadata:
   - **Name**: meegle-mcp
   - **Description**: Integrate Meegle project management with OpenClaw
   - **Category**: Productivity / Project Management
   - **Tags**: meegle, project-management, mcp, larksuite, workflow
6. Submit for review

### 4. Maintain Your Skill

After publishing:

- Use semantic versioning for updates (v1.0.0, v1.1.0, etc.)
- Update `CHANGELOG.md` with release notes
- Respond to issues and pull requests
- Keep dependencies updated

### Example Publishing Workflow

```bash
# Make changes
git add .
git commit -m "feat: Add bulk task creation support"

# Tag release
git tag -a v1.1.0 -m "Version 1.1.0: Bulk task creation"
git push origin v1.1.0

# Publish to ClawHub
clawhub publish --version 1.1.0
```

## Security Best Practices

- 🔒 **Never commit credentials** to version control
- 🔒 Use `.gitignore` to exclude sensitive files
- 🔒 Store keys in environment variables or secure vaults
- 🔒 Keep both `MEEGLE_USER_KEY` and `MEEGLE_MCP_KEY` secure
- 🔒 Consider using a dedicated service account for OpenClaw
- 🔒 Review and limit MCP server permissions
- 🔒 Regularly rotate your User Key and MCP Key

## Project Structure

```
meegle-mcp-skill/
├── SKILL.md                     # Main skill definition
├── README.md                    # This file
├── LICENSE                      # License file
├── mcp-config.example.json      # Example configuration
├── .gitignore                   # Git ignore patterns
└── scripts/
    ├── mcp-proxy.js            # MCP protocol proxy
    └── setup.sh                # Automated setup script
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit a pull request

## Resources

- [Meegle Official Site](https://www.meegle.com/)
- [Meegle Documentation](https://www.larksuite.com/hc/en-US/articles/040270863407-meegle-overview)
- [OpenClaw Documentation](https://docs.openclaw.ai/)
- [ClawHub](https://clawhub.ai/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- 🐛 [Report Issues](https://github.com/pkycy/meegle-mcp-skill/issues)
- 💬 [Discuss on ClawHub](https://clawhub.ai/skills/meegle-mcp)
- 📧 Email: 13060626770@163.com

---

**Made with ❤️ for the OpenClaw community**
