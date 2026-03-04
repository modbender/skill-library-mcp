# ClawHub Publisher

**Value Proposition**: Automated skill publishing to ClawHub. Version management, changelog generation, asset bundling, instant deployment.

## Problem Solved
- Manual skill publishing is tedious
- Version tracking & changelog generation
- Asset bundling complexity
- Deployment to ClawHub not automated
- Need for CI/CD integration

## Use Cases
- Automatic skill versioning & deployment
- One-command publish workflow
- Changelog auto-generation
- Multi-file asset bundling
- Gumroad integration & upsell linking
- Skill stats & analytics dashboard
- Rolling back bad deployments
- Team publishing workflows

## Quick Start

```bash
npm install clawhub-publisher
# or
python -m pip install clawhub-publisher
```

```javascript
const Publisher = require('clawhub-publisher');

const publisher = new Publisher({
  apiKey: process.env.CLAWHUB_API_KEY,
  author: 'Your Name',
  gumroadLink: 'https://gumroad.com/your-product'
});

// Publish current skill
const result = await publisher.publish({
  skillPath: './my-skill',
  version: '1.0.0',
  changelog: 'Initial release with core features'
});

console.log('Published to:', result.clawHubUrl);
```

## Features
✅ One-command skill publishing
✅ Automatic version bumping (major/minor/patch)
✅ Git-powered changelog generation
✅ Multi-file asset bundling
✅ Metadata validation
✅ README optimization
✅ Gumroad link injection
✅ Publishing history & rollback
✅ Skill analytics
✅ Team collaboration support
✅ CI/CD integration (GitHub Actions, etc.)

## Installation

### Node.js
```bash
npm install clawhub-publisher
```

### Python
```bash
pip install clawhub-publisher
```

### CLI
```bash
npm install -g clawhub-publisher
clawhub-publisher --version
clawhub-publisher login --token YOUR_API_KEY
```

## Configuration

```javascript
const publisher = new Publisher({
  apiKey: 'ch-...',  // Get from ClawHub dashboard
  author: 'Midas Skills',
  gumroadLink: 'https://gumroad.com/midas-skills',
  workspace: './skills',
  dryRun: false  // Preview changes without publishing
});
```

## Example Code

### Basic Single Skill Publish
```javascript
const Publisher = require('clawhub-publisher');
const publisher = new Publisher();

const result = await publisher.publish({
  skillPath: './skills/my-skill',
  version: '1.0.0',
  changelog: 'Initial release'
});

console.log(`✅ Published ${result.skillName}`);
console.log(`📦 ClawHub URL: ${result.clawHubUrl}`);
console.log(`📥 Install: npm install ${result.packageName}`);
```

### Auto-Bump Version & Generate Changelog
```javascript
// Automatically determines next version based on git commits
const result = await publisher.publish({
  skillPath: './skills/my-skill',
  autoBump: true,  // Analyzes commits for feat/fix/breaking
  autoChangelog: true  // Generates from commit messages
});

// If you had commits:
//   - "feat: add new feature" → bumps MINOR
//   - "fix: bug fix" → bumps PATCH
//   - "BREAKING CHANGE" → bumps MAJOR
```

### Batch Publish Multiple Skills
```javascript
const skills = [
  'resilient-file-delivery',
  'browser-automation-stealth',
  'marketing-drafter',
  'agentmail-wrapper'
];

const results = await publisher.publishBatch({
  skillPaths: skills.map(s => `./skills/${s}`),
  autoBump: true,
  autoChangelog: true,
  parallel: 2  // Publish 2 at a time
});

console.log(`✅ Published ${results.succeeded}/${results.total} skills`);
results.published.forEach(s => {
  console.log(`  - ${s.name}: ${s.clawHubUrl}`);
});
```

### Gumroad Link Injection
```javascript
// Automatically injects Gumroad upsell link into README
const result = await publisher.publish({
  skillPath: './my-skill',
  version: '1.0.0',
  gumroadLink: 'https://gumroad.com/your-bundle',
  gumroadText: 'Want pro version + updates? Buy bundle on Gumroad'
});

// README.md will have:
// ---
// **Want pro version + updates?** [Buy bundle on Gumroad](https://gumroad.com/your-bundle)
```

### Pre-publish Validation
```javascript
// Check if skill is ready before publishing
const validation = await publisher.validate({
  skillPath: './my-skill'
});

if (!validation.isValid) {
  console.log('❌ Validation failed:');
  validation.errors.forEach(e => console.log(`  - ${e.message}`));
} else {
  console.log('✅ Ready to publish!');
  console.log('  - package.json: OK');
  console.log('  - README.md: OK');
  console.log('  - Examples: OK');
}
```

### Publishing with GitHub Actions
```yaml
name: Publish Skill to ClawHub
on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install clawhub-publisher
      - run: npx clawhub-publisher publish \
          --api-key ${{ secrets.CLAWHUB_API_KEY }} \
          --skill-path ./my-skill \
          --version ${GITHUB_REF#refs/tags/v}
```

### View Publishing History & Rollback
```javascript
const publisher = new Publisher();

// Get publishing history
const history = await publisher.getHistory({ skillName: 'my-skill' });
console.log(history);
// [
//   { version: '1.0.2', publishedAt: '2024-02-10', status: 'published' },
//   { version: '1.0.1', publishedAt: '2024-02-09', status: 'published' },
//   { version: '1.0.0', publishedAt: '2024-02-08', status: 'published' }
// ]

// Rollback to previous version
await publisher.rollback({
  skillName: 'my-skill',
  targetVersion: '1.0.1'
});
```

### Skill Analytics
```javascript
const stats = await publisher.getStats({
  skillName: 'my-skill'
});

console.log('Downloads:', stats.totalDownloads);
console.log('Active users:', stats.activeUsers);
console.log('Avg rating:', stats.avgRating);
console.log('Recent reviews:', stats.recentReviews);
```

### Team Collaboration
```javascript
// Add team member access
await publisher.addTeamMember({
  skillName: 'my-skill',
  email: 'teammate@example.com',
  role: 'publisher'  // 'viewer', 'editor', 'publisher'
});

// View team members
const team = await publisher.getTeam({ skillName: 'my-skill' });
console.log('Team:', team);
```

## CLI Commands

```bash
# Login to ClawHub
clawhub-publisher login --token YOUR_API_KEY

# Publish single skill
clawhub-publisher publish --skill-path ./my-skill --version 1.0.0

# Auto-bump version and publish
clawhub-publisher publish --skill-path ./my-skill --auto-bump

# Batch publish
clawhub-publisher publish-batch --dir ./skills

# Validate skill
clawhub-publisher validate --skill-path ./my-skill

# View history
clawhub-publisher history --skill-name my-skill

# Rollback
clawhub-publisher rollback --skill-name my-skill --version 1.0.0

# Get stats
clawhub-publisher stats --skill-name my-skill
```

## Required Skill Structure

```
my-skill/
├── README.md              # With value prop, use cases, examples
├── package.json           # With clawhub metadata
├── index.js (or main file)
├── examples/              # Example code (optional)
├── docs/                  # Documentation (optional)
└── CHANGELOG.md           # Auto-generated or manual
```

## package.json clawhub Metadata

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Short description",
  "clawhub": {
    "category": "automation",
    "tags": ["tag1", "tag2"],
    "skillType": "integration",
    "price": "0",
    "proPrice": "29.99"
  }
}
```

## API Reference

### `publish(options)`
Publish skill to ClawHub.
- `skillPath` (string): Path to skill directory
- `version` (string): Version (e.g., '1.0.0')
- `changelog` (string): What changed
- `autoBump` (boolean): Auto-increment version
- `autoChangelog` (boolean): Generate changelog from git
- Returns: `Promise<{skillName, version, clawHubUrl}>`

### `publishBatch(options)`
Publish multiple skills.
- `skillPaths` (array): Array of skill paths
- `autoBump` (boolean): Auto-bump all
- `parallel` (number): Concurrent publishes
- Returns: `Promise<{succeeded, failed, published}>`

### `validate(options)`
Validate skill before publishing.
- Returns: `Promise<{isValid, errors, warnings}>`

## Troubleshooting

**"Authentication failed"?**
→ Run `clawhub-publisher login` with correct API key

**"Skill validation failed"?**
→ Run `clawhub-publisher validate --skill-path ./my-skill`

**Missing required fields?**
→ Ensure package.json has `clawhub` metadata block

## Support
📧 support@midas-skills.com
🔗 Docs: https://docs.midas-skills.com/clawhub-publisher

---

**Want pro version + updates?** [Buy bundle on Gumroad](https://gumroad.com/midas-skills)
