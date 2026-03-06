---
name: azion-deploy
description: Deploy applications, static sites, and edge functions to Azion using Azion CLI. Use when the user asks to deploy/publish to Azion, configure link/build/deploy flow, or troubleshoot Azion auth/project linking problems.
version: 0.1.1
author: AskClaw
entrypoint: scripts/azion-deploy.sh
metadata: {"openclaw":{"emoji":"🚀","short":"Deploy to Azion (CLI)","requires":{"bins":["bash","azion"]}}}
user-invocable: true
command-dispatch: tool
command-tool: azion-deploy
commands:
  - name: azion-deploy
    usage: azion-deploy <preflight|auth-check|quickstart|deploy-local> [args]
    description: Deploy helper wrapper around azion CLI with preflight/auth checks.
---
# azion-deploy

Use this skill to deploy projects to Azion with safe preflight checks.

## Built-in checks

The script fails fast if:
- `azion` executable is missing
- authentication fails (`azion whoami`)
- `.edge/manifest.json` is missing when using `--skip-build`

## Commands

```bash
# Validate CLI + auth
bash {baseDir}/scripts/azion-deploy.sh preflight

# Validate auth only
bash {baseDir}/scripts/azion-deploy.sh auth-check

# Stable quickstart flow
bash {baseDir}/scripts/azion-deploy.sh quickstart --name <project-name> [--token "$AZION_TOKEN"]

# Local deploy flow
bash {baseDir}/scripts/azion-deploy.sh deploy-local [--skip-build] [--auto] [--token "$AZION_TOKEN"]
```

## Notes

- Keep `link -> build -> deploy` sequential (never parallel).
- If `whoami` fails, run `azion login` (interactive) or provide valid `AZION_TOKEN`.
- For detailed flags and framework behavior, read:
  - `references/azion-cli.md`
  - `references/azion-build-frameworks.md`
