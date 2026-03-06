# Checkly CLI Skills

A comprehensive collection of skills for AI coding agents to use the Checkly CLI effectively. These skills enable agents to implement Monitoring as Code (MaC) workflows for synthetic monitoring.

## What is Checkly?

[Checkly](https://www.checklyhq.com/) is a monitoring platform that enables Monitoring as Code. The Checkly CLI provides a TypeScript/JavaScript-native workflow for coding, testing, and deploying synthetic monitoring at scale.

## Installation

```bash
npx skills add vince-winkintel/checkly-cli-skills
```

## Available Skills

### Getting Started
- **[checkly-auth](./checkly-auth)** - Authentication and login
- **[checkly-config](./checkly-config)** - Configuration files and project setup

### Core Workflows
- **[checkly-test](./checkly-test)** - Local testing with `npx checkly test`
- **[checkly-deploy](./checkly-deploy)** - Deployment to Checkly cloud
- **[checkly-import](./checkly-import)** - Import existing checks from UI to code

### Check Types
- **[checkly-checks](./checkly-checks)** - API checks, browser checks, multi-step checks
- **[checkly-monitors](./checkly-monitors)** - Heartbeat, TCP, DNS, URL monitors
- **[checkly-groups](./checkly-groups)** - Check groups and organization

### Advanced Topics
- **[checkly-constructs](./checkly-constructs)** - Constructs system and resource management
- **[checkly-playwright](./checkly-playwright)** - Playwright test suites
- **[checkly-advanced](./checkly-advanced)** - Retry strategies, reporters, environment variables

## Quick Start

Example prompts for AI agents:

- "Set up Checkly CLI authentication"
- "Create an API check for https://api.example.com/status"
- "Create a Playwright browser check for login flow"
- "Test all checks locally before deploying"
- "Deploy checks to Checkly cloud"
- "Import existing checks from Checkly UI"
- "Configure retry strategy for failed checks"

## Templates

The [`templates/`](./templates) directory includes ready-to-use templates:

- **API Checks**: Basic and authenticated patterns
- **Browser Checks**: Homepage and login flow patterns
- **Configuration**: Basic and advanced checkly.config.ts examples
- **Monitors**: Heartbeat and health check patterns
- **Check Groups**: Organization and shared configuration patterns

## Scripts

The [`scripts/`](./scripts) directory provides automation helpers:

- `init-project.sh` - Initialize new Checkly project
- `test-and-deploy.sh` - Test locally before deploying
- `import-from-ui.sh` - Import existing checks from UI
- `validate-config.sh` - Validate project configuration

## References

The [`references/`](./references) directory contains:

- **best-practices.md** - Project organization, naming conventions, security
- **troubleshooting.md** - Common issues and solutions

## Prerequisites

- **Checkly Account**: Sign up at [checklyhq.com/signup](https://www.checklyhq.com/signup)
- **Node.js**: Version 18 or higher
- **Checkly CLI**: Installed via `npm create checkly@latest` or `npm install -g checkly`

## Install Checkly CLI

```bash
# Create new project (recommended)
npm create checkly@latest

# Or install globally
npm install -g checkly

# Or use with npx (no installation)
npx checkly --help
```

## Example Workflow

```bash
# 1. Create project
npm create checkly@latest my-monitoring
cd my-monitoring

# 2. Authenticate
npx checkly login

# 3. Create checks (see templates/)
cat > __checks__/api.check.ts << 'EOF'
import { ApiCheck, AssertionBuilder } from 'checkly/constructs'

new ApiCheck('api-status', {
  name: 'API Status Check',
  request: {
    url: 'https://api.example.com/status',
    method: 'GET',
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.responseTime().lessThan(500),
    ],
  },
})
EOF

# 4. Test locally
npx checkly test

# 5. Deploy to production
npx checkly deploy
```

## Documentation

- [Checkly CLI Documentation](https://www.checklyhq.com/docs/cli/)
- [Monitoring as Code Guide](https://www.checklyhq.com/docs/monitoring-as-code/)
- [Playwright Documentation](https://playwright.dev/)
- [Checkly Runtimes](https://www.checklyhq.com/docs/runtimes/)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with an AI agent
5. Submit a pull request

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Acknowledgments

- Built for AI coding agents following the [Agent Skills](https://github.com/cyanheads/agent-skills) format
- Inspired by the [gitlab-cli-skills](https://github.com/vince-winkintel/gitlab-cli-skills) project
- Based on official [Checkly CLI](https://github.com/checkly/checkly-cli) by Checkly

## Support

- [Checkly Community](https://community.checklyhq.com/)
- [GitHub Issues](https://github.com/vince-winkintel/checkly-cli-skills/issues)
- [Checkly Support](https://www.checklyhq.com/support/)

---

Built with ❤️ for AI coding agents
