---
name: opencode-omo
version: 0.3.0
description: Turn coding requests into completed work. Plan with Prometheus, execute with Atlas, and iterate with Sisyphus in OpenCode.
homepage: https://github.com/IISweetHeartII/opencode-omo
metadata:
  openclaw:
    emoji: "🧱"
    category: devtools
    requires:
      bins:
        - opencode
        - git
        - clawhub
    tags:
      - opencode
      - oh-my-opencode
      - sisyphus
      - coding
      - workflow
---

# OpenCode + Oh-My-OpenCode Operator

This skill is an operating guide for using **OpenCode** as your coding runtime, with **Oh-My-OpenCode** orchestration through Sisyphus, Prometheus, and Atlas.

## What this skill gives you

- One-shot delivery with `ulw` for focused coding requests.
- Plan-to-execution workflow via `@plan` and `/start-work`.
- Repeatable defaults so code quality stays consistent across runs.

## Core rules

- Do not edit code directly outside OpenCode unless explicitly asked.
- Prefer Sisyphus-first execution for coding tasks.
- For complex work: plan with Prometheus (`@plan`) then execute with Atlas (`/start-work`).

## Quick start

### Verify Oh-My-OpenCode plugin

```bash
cat ~/.config/opencode/opencode.json | grep "oh-my-opencode"
```

If the command returns output, the plugin is installed.

You can also run the bundled checker:

```bash
./scripts/check-omo.sh
```

### Run one-shot coding (Sisyphus + ultrawork)

```bash
opencode run --agent sisyphus "ulw implement JWT auth in this service and add tests"
```

Or use the bundled helper:

```bash
./scripts/run-ulw.sh "implement JWT auth in this service and add tests"
```

### Start interactive OpenCode (Sisyphus)

```bash
opencode --agent sisyphus
```

Inside OpenCode:

- Use `@plan "..."` to invoke Prometheus planning.
- Use `/start-work` to let Atlas execute the plan.

## Failure handling

- If the agent asks clarifying questions mid-implementation, answer them in plan mode (Prometheus) and re-run execution.
- If you need more determinism, re-run with `ulw` and a smaller, explicit request.

## Integration with other skills

- **[agent-selfie](https://clawhub.org/skills/agent-selfie)**: pair structured coding workflows with generated visual assets.
- **[gemini-image-gen](https://clawhub.org/skills/gemini-image-gen)**: use the same workflow discipline for image generation automations.
- **[agentgram](https://clawhub.org/skills/agentgram)**: publish progress updates, findings, and demos produced from your workflow runs.

## Changelog

- v0.3.0: Added bidirectional ecosystem links and bundled workflow helper scripts.
- v0.2.0: Reworked positioning, quick start, and metadata for clearer marketplace onboarding.
- v0.1.0: Initial release with Sisyphus/Prometheus/Atlas workflow guidance.
