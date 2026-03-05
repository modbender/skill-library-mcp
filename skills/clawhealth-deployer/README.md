# ClawHealth Deployer (ClawHub Skill)

This folder is a [ClawHub](https://clawhub.ai/) skill. It teaches OpenClaw how to deploy ClawHealth on the user’s machine and connect it via MCP so the assistant can query health data in chat.

## Install this skill (for OpenClaw users)

If you use ClawHub:

```bash
clawhub install clawhealth-deployer
```

(or search for “ClawHealth” / “health data” on [clawhub.ai](https://clawhub.ai/) and install from there).

Then in OpenClaw, say e.g. “Deploy ClawHealth and connect it to OpenClaw” and the agent will run the install script and merge MCP config.

## Publish this skill (for maintainers)

From this folder:

```bash
clawhub publish . --slug clawhealth-deployer --name "ClawHealth Deployer" --version 1.0.0 --tags latest
```

(Requires `clawhub login` first.)

## Contents

- **SKILL.md** — Skill description and instructions for the agent.
- **scripts/install.sh** — Clones repo (if needed), runs `make deploy-openclaw`, merges MCP into `~/.clawdbot/clawdbot.json5`.
- **scripts/merge-mcp.js** — Node script to merge the open-wearables MCP server into the config file.
- **package.json** — Dependency for `merge-mcp.js` (json5).
