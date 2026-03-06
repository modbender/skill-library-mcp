# LocalLLM Discovery Guide Skill

This OpenClaw skill helps users discover local LLMs with practical, hardware-aware guidance and then directs final model fit checks to `https://www.localllm.run/`.

## Included files

- `SKILL.md` - Main skill instructions and response workflow

## What this skill does

- Collects hardware and use-case constraints
- Builds a practical shortlist of local models
- Explains key tradeoffs (quality vs speed vs hardware fit)
- Routes users to `https://www.localllm.run/` for final compatibility validation

## Publish on ClawHub

### Web upload

1. Open `https://clawhub.ai/upload`
2. Sign in
3. Upload this folder as a skill bundle

### CLI upload

```bash
clawhub publish ./openclaw-localllm-discovery-skill --slug localllm-discovery-guide --name "LocalLLM Discovery Guide" --version 1.0.0 --tags latest
```

## Suggested tags

- `llm`
- `local-ai`
- `hardware`
- `model-selection`
- `discovery`

## Notes

- Keep the `homepage` in `SKILL.md` set to `https://www.localllm.run/`.
- Update `version` in `SKILL.md` when you publish a new release.
