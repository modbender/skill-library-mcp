# @skillforge/github-automation

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://www.npmjs.com/package/@skillforge/github-automation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

OpenClaw Skill for GitHub automation - Issues, PRs, and Releases made easy.

## Features

- 🐛 **Issue Automation** - Create, list, and update issues with labels and assignees
- 🔍 **PR Analysis** - Get insights on PR size, risk, and suggestions
- 📝 **Review Assistant** - Generate review checklists for pull requests
- 🏷️ **Release Management** - Auto-generate release notes and publish releases
- 📊 **Repo Analytics** - Get repository stats and health assessments

## Quick Start

```typescript
import { createGitHubSkill, SkillConfigBuilder } from '@skillforge/github-automation';

const config = new SkillConfigBuilder()
  .setGitHubToken(process.env.GITHUB_TOKEN)
  .setDefaultOwner('myorg')
  .setDefaultRepo('myrepo')
  .enableAllFeatures()
  .build();

const skill = createGitHubSkill();
await skill.initialize(config);

// Create an issue
const result = await skill.execute({
  action: 'issue.create',
  params: {
    title: 'Bug: Login not working',
    body: 'Users cannot log in...',
    labels: ['bug', 'urgent'],
  },
});
```

## Installation

```bash
npm install @skillforge/github-automation
```

## Documentation

See [SKILL.md](./SKILL.md) for detailed documentation.

## Architecture

This skill uses several design patterns:

- **Builder Pattern** - For constructing configuration objects
- **Strategy Pattern** - For different execution strategies
- **Factory Pattern** - For creating skill instances

## License

MIT © SkillForge
