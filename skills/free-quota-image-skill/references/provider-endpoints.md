# Provider Endpoints

Use this reference when extending or debugging API wiring.

## Hugging Face (public HF Spaces)

* `https://luca115-z-image-turbo.hf.space`
  * Queue join: `POST /gradio_api/queue/join`
  * Queue stream: `GET /gradio_api/queue/data?session_hash=...`
  * Model: `z-image-turbo`
  * Data: `[prompt, height, width, steps, seed, false]`

* `https://mrfakename-z-image.hf.space`
  * Model: `z-image`
  * Data: `[prompt, negative_prompt, height, width, steps, guidance, seed, false]`

* `https://mcp-tools-qwen-image-fast.hf.space`
  * Model: `qwen-image`
  * Data: `[prompt, seed, randomize_seed, aspect_ratio, 3, steps]`

* `https://aidc-ai-ovis-image-7b.hf.space`
  * Model: `ovis-image`
  * Data: `[prompt, height, width, seed, steps, 4]`

* `https://black-forest-labs-flux-1-schnell.hf.space`
  * Model: `flux-1-schnell`
  * Data: `[prompt, seed, false, width, height, steps]`

Notes:

* Token is optional. Use `Authorization: Bearer <token>` when available.
* Quota exhaustion is detected by HTTP 429 or quota keywords in stream messages.

## Gitee AI

* Image generation: `POST https://ai.gitee.com/v1/images/generations`
* Required header: `Authorization: Bearer <token>`
* Payload:
  * `prompt`, `model`, `width`, `height`, `seed`, `num_inference_steps`
  * optional `guidance_scale`
  * `response_format: url`

## ModelScope

* Create task: `POST https://api-inference.modelscope.cn/v1/images/generations`
  * Headers:
    * `Authorization: Bearer <token>`
    * `X-ModelScope-Async-Mode: true`
  * Payload:
    * `prompt`, `model`, `size`, `seed`, `steps`, optional `guidance`

* Poll task: `GET https://api-inference.modelscope.cn/v1/tasks/{task_id}`
  * Header: `X-ModelScope-Task-Type: image_generation`

## A4F

* Image generation: `POST https://api.a4f.co/v1/images/generations`
* Required header: `Authorization: Bearer <token>`
* Payload:
  * `model`, `prompt`, `n: 1`, `size`, `response_format: url`

## OpenAI-compatible (private paid fallback)

* Base URL comes from `providers.openai_compatible.api_url`.
  * SiliconFlow example: `https://api.siliconflow.cn/v1`
* Image endpoint comes from `providers.openai_compatible.images_endpoint` (default `/images/generations`).
* Required header: `Authorization: Bearer <token>`
* Payload:
  * `model`, `prompt`, `size`, `n: 1`, `response_format: url`, `seed`
  * Supported model examples: `Qwen/Qwen-Image`, `Kwai-Kolors/Kolors`
* Response parsing:
  * Prefer `data[0].url`
  * Fallback to `data[0].b64_json` converted into a `data:image/png;base64,...` URL

## Prompt optimization endpoints

* Hugging Face path uses Pollinations OpenAI-compatible API:
  * `POST https://text.pollinations.ai/openai`
* Gitee:
  * `POST https://ai.gitee.com/v1/chat/completions`
* ModelScope:
  * `POST https://api-inference.modelscope.cn/v1/chat/completions`
* A4F:
  * `POST https://api.a4f.co/v1/chat/completions`

