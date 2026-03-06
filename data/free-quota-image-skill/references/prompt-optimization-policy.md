# Prompt Optimization Policy

## Pipeline

Prompt processing runs before each generation attempt:

1. optional auto-translate
2. optional prompt optimization
3. generation request

Both processing stages are fail-open by default:

* on error, keep previous prompt text
* continue generation

## Optimization system prompt

Final optimization instruction:

* `prompt_optimization.system_prompt`
* plus fixed suffix requiring output language consistency

This mirrors the Peinture behavior where a fixed language constraint is always appended.

## Provider model defaults

Configured at:

`prompt_optimization.default_model_by_provider`

Default values:

* huggingface: `openai-fast` (via Pollinations)
* gitee: `deepseek-3_2`
* modelscope: `deepseek-3_2`
* a4f: `gemini-2.5-flash-lite`

## Auto translation

Controls:

* CLI: `--auto-translate` / `--no-auto-translate`
* Config: `translation.enabled`
* Config model list: `translation.target_models`

Translation runs only when all are true:

* CLI auto-translate is enabled
* config translation is enabled
* selected model is in `translation.target_models`

## API notes

* Hugging Face optimization and translation both use `https://text.pollinations.ai/openai`.
* Gitee/ModelScope/A4F optimization use each provider's chat completions endpoint with provider token.
* OpenAI-compatible image fallback currently skips optimization and uses the prepared prompt directly.

