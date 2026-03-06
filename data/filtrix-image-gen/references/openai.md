# OpenAI Image Generation

## Model: gpt-image-1

- Endpoint: `POST https://api.openai.com/v1/images/generations`
- Returns base64-encoded PNG by default
- Sizes: `1024x1024`, `1536x1024`, `1024x1536`, `auto`
- `auto` lets the model choose the best size for the prompt

## Safety Filters

OpenAI applies content safety filtering. If a prompt is rejected, the API returns HTTP 400 with a message containing "safety system". Modify the prompt to be less explicit and retry.

## Cost

gpt-image-1 pricing varies by size. Check platform.openai.com/pricing for current rates.

## Tips

- Adding "high quality, detailed, 4k" tends to improve output
- For consistent characters, describe the character in detail each time
- Negative prompts are not natively supported; rephrase as positive instructions
