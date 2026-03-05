# Available GitHub Copilot Models - Detailed Specs

Based on GitHub Copilot model specifications.

## Claude Models (Anthropic)
- **Claude Haiku 4.5**: Context 128K/32K, Tools+Vision, 0.33x multiplier (fast, cheap)
- **Claude Opus 4.5**: Context 128K/32K, Tools+Vision, 3x multiplier (powerful, expensive)
- **Claude Opus 4.6**: Context 128K/64K, Tools+Vision, 3x multiplier (latest Opus, high output)
- **Claude Sonnet 4**: Context 128K/16K, Tools+Vision, 1x multiplier (balanced)
- **Claude Sonnet 4.5**: Context 128K/32K, Tools+Vision, 1x multiplier (current Sonnet)

## Gemini Models (Google)
- **Gemini 2.5 Pro**: Context 109K/64K, Tools+Vision, 1x multiplier (high performance)
- **Gemini 3 Flash (Preview)**: Context 109K/64K, Tools+Vision, 0.33x multiplier (fast, preview)
- **Gemini 3 Pro (Preview)**: Context 109K/64K, Tools+Vision, 1x multiplier (advanced, preview)

## GPT Models (OpenAI)
- **GPT-4.1**: Context 111K/16K, Tools+Vision, 0x multiplier (free?)
- **GPT-4o**: Context 64K/4K, Tools+Vision, 0x multiplier (free, classic)
- **GPT-5**: Context 128K/128K, Tools+Vision, 1x multiplier (latest, balanced)
- **GPT-5 mini**: Context 128K/64K, Tools+Vision, 0x multiplier (fast mini)
- **GPT-5-Codex (Preview)**: Context 128K/128K, Tools+Vision, 1x multiplier (code-focused)
- **GPT-5.1**: Context 128K/64K, Tools+Vision, 1x multiplier (improved)
- **GPT-5.1-Codex**: Context 128K/128K, Tools+Vision, 1x multiplier (code)
- **GPT-5.1-Codex-Max**: Context 128K/128K, Tools+Vision, 1x multiplier (max code)
- **GPT-5.1-Codex-Mini (Preview)**: Context 128K/128K, Tools+Vision, 0.33x multiplier (mini code)
- **GPT-5.2**: Context 128K/64K, Tools+Vision, 1x multiplier (next gen)
- **GPT-5.2-Codex**: Context 272K/128K, Tools+Vision, 1x multiplier (huge context code)

## Other
- **Grok Code Fast 1**: Context 109K/64K, Tools, 0x multiplier (free, fast code)
- **Raptor mini (Preview)**: Context 200K/64K, Tools+Vision, 0x multiplier (preview, large context)

## Selection Guidelines
- **Cost**: Lower multiplier = cheaper/faster (0.33x cheapest, 3x most expensive)
- **Context**: Higher numbers better for long tasks
- **Use**: Code tasks -> Codex variants; Vision -> models with Vision; Tools for function calling
- **Free**: 0x multiplier models
- **Paid**: 0.33x to 3x

## Cost Considerations
- Multiplier indicates relative cost per request
- Free models have 0x, no usage costs
- Paid models scale with multiplier