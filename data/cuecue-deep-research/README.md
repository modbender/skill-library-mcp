# CueCue Deep Research Skill

This repository contains the ClawdHub skill definition for CueCue Deep Research.

## Publishing to ClawdHub

The skill is automatically published to ClawdHub when a new release is created.

### Automatic Publishing (Recommended)

1. Create a new release on GitHub:
   ```bash
   git tag 1.0.6
   git push origin 1.0.6
   ```

2. Go to GitHub Releases and create a new release from the tag

3. The workflow will automatically:
   - Update the version in SKILL.md
   - Validate the SKILL.md file
   - Publish to ClawdHub

### Manual Publishing

You can also trigger the workflow manually:

1. Go to Actions → "Publish to ClawdHub"
2. Click "Run workflow"
3. Enter the version number (e.g., `1.0.6`)
4. Click "Run workflow"

## Setup

Before publishing, ensure you have set up the `CLAWHUB_TOKEN` secret in your GitHub repository:

1. Get your ClawHub API token:
   - Visit https://clawhub.ai
   - Login with your GitHub account
   - Go to Settings → API Tokens
   - Generate a new token

2. Add the token to GitHub:
   - Go to your repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CLAWHUB_TOKEN`
   - Value: Your ClawHub API token
   - Click "Add secret"

## Skill Details

- **Name**: cuecue-deep-research
- **Description**: Conduct deep financial research using CueCue's AI-powered multi-agent system
- **Current Version**: 1.0.5
- **Homepage**: https://cuecue.cn

## Development

To update the skill:

1. Edit `SKILL.md` with your changes
2. Update the version number in the frontmatter
3. Commit and push your changes
4. Create a new release to publish

## License

See [LICENSE](LICENSE) file for details.
