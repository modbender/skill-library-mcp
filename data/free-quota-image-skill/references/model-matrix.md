# Model Matrix

## Generation models by provider

| Provider    | Supported models                                                                   |
| ----------- | ---------------------------------------------------------------------------------- |
| huggingface | `z-image-turbo`, `z-image`, `qwen-image`, `ovis-image`, `flux-1-schnell`           |
| gitee       | `z-image-turbo`, `qwen-image`, `flux-2`, `flux-1-schnell`, `flux-1-krea`, `flux-1` |
| modelscope  | `z-image-turbo`, `z-image`, `flux-2`, `flux-1-krea`, `flux-1`                      |
| a4f         | `z-image-turbo`, `imagen-4`, `imagen-3.5`                                          |
| openai_compatible | `Qwen/Qwen-Image`, `Kwai-Kolors/Kolors`                            |

## Fallback model chain

For each provider, model resolution is deterministic:

1. requested model
2. `z-image-turbo`
3. provider default model (first model in provider list)

Any unsupported item is skipped.

## Prompt optimization default text models

| Provider    | Model key               |
| ----------- | ----------------------- |
| huggingface | `openai-fast`           |
| gitee       | `deepseek-3_2`          |
| modelscope  | `deepseek-3_2`          |
| a4f         | `gemini-2.5-flash-lite` |

## Auto-translate target models (default)

* `flux-1-schnell`
* `flux-1-krea`
* `flux-1`
* `flux-2`

## HD scaling rules

* General: 2x multiplier
* Gitee + Flux models: 1.5x multiplier

