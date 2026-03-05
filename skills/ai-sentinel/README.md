# AI Sentinel - ClawHub Skill

This folder contains the ClawHub skill package for AI Sentinel. It provides an interactive setup wizard that helps OpenClaw users integrate prompt injection protection into their gateway.

## Folder Structure

```
packages/clawhub-skill/
├── SKILL.md        # Skill entry point (required by ClawHub)
├── CHANGELOG.md    # Version history (required by ClawHub publish form)
└── README.md       # This file (developer reference)
```

## Publishing to ClawHub

1. Go to the ClawHub publish page
2. Fill in the **required form fields**:

   | Field        | Value                                       |
   |--------------|---------------------------------------------|
   | Slug         | `ai-sentinel`                               |
   | Display name | `AI Sentinel - Prompt Injection Firewall`   |
   | Version      | `1.2.0`                                     |
   | Tags         | `security`, `prompt-injection`, `firewall`, `middleware` |

3. Fill in **registry metadata fields** (these must match what SKILL.md declares, or the security scan will flag a mismatch):

   | Registry Field       | Value |
   |----------------------|-------|
   | Required env vars    | `AI_SENTINEL_API_KEY` (optional, Pro tier only) |
   | Required config      | `openclaw.config.ts` |
   | External services    | `https://api.zetro.ai` (Pro tier only) |
   | Installed packages   | `ai-sentinel-sdk` |
   | Files written        | `openclaw.config.ts`, `.env`, `data/`, `.gitignore` |

4. Upload this entire `clawhub-skill/` folder
5. Paste the contents of `CHANGELOG.md` into the Changelog field
6. Submit

**Important:** If the registry form does not have dedicated fields for env vars / external services / config paths, add them to the description or notes field. The OpenClaw security scanner compares registry metadata against SKILL.md content and flags mismatches.

## Testing

To manually test the skill before publishing:

1. Open an OpenClaw project that has `openclaw.config.ts`
2. Copy `SKILL.md` into the project's `.openclaw/skills/` directory (or wherever the local skill override path is)
3. Invoke the skill and walk through the setup wizard
4. Verify:
   - `ai-sentinel-sdk` is installed in `node_modules`
   - `openclaw.config.ts` has the sentinel middleware wired up
   - `npx openclaw sentinel test "Ignore all previous instructions"` returns a `blocked` action
   - `npx openclaw sentinel test "Hello, how are you?"` returns an `allowed` action
   - `npx openclaw sentinel status` displays the correct tier and config

## Updating

When releasing a new version:

1. Update the version in `SKILL.md` header (the `**Version:**` field)
2. Add a new section to `CHANGELOG.md` with the changes
3. Re-upload the folder to ClawHub with the new version number in the publish form

## Dependencies

The skill instructs users to install `ai-sentinel-sdk` (published to npm). Ensure the SDK is published and up-to-date before publishing a new skill version that references new SDK features.

## Related Files

- `packages/sdk-node/` - The `ai-sentinel-sdk` Node.js package
- `packages/sdk-node/src/middleware/openclaw.ts` - OpenClaw middleware implementation
- `packages/sdk-node/src/types.ts` - `SentinelConfig` interface (the config shape the skill generates)
- `packages/sdk-node/src/cli/index.ts` - CLI commands referenced in the test step
- `.claude/commands/setup-sentinel.md` - The older Python SDK setup wizard (separate from this skill)
