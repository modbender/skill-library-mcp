# Changelog

## 1.0.0 (2026-02-17)

Initial public release.

### Features
- One-shot deploy: VPC + EC2 (ARM64) + OpenClaw + Telegram in a single command
- SSM-only access (no SSH, no inbound ports)
- Configurable AI model: Bedrock (default, no API key), Gemini, or any provider
- 5 personality presets (default, sentinel, researcher, coder, companion)
- Auto-rollback on failed deploys
- Clean teardown with tag verification and dry-run mode
- IAM setup helper with least-privilege policy
- Preflight validation and post-deploy smoke test
- 22 documented issues with solutions baked into scripts

### Security
- Secrets stored in AWS SSM Parameter Store (fetched at runtime)
- Encrypted EBS volumes
- IMDSv2 enforced
- SHA256 verification on Node.js tarball
- Input validation on all CLI arguments
- No hardcoded credentials
