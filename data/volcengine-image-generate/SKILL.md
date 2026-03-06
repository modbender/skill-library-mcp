---
name: volcengine-image-generate
description: Using volcengine image_generate.py script to generate image, need to provide clear and specific `prompt`.
license: Complete terms in LICENSE.txt
---

# Image Generate

## Scenarios

When you need to generate an image based on a text description, use this skill to call the `image_generate` function.

## Steps

1. Prepare a clear and specific `prompt`.
2. Run the script `python scripts/image_generate.py "<prompt>"`. Before running, navigate to the corresponding directory.
3. The script will return the generated image URL.

## Authentication and Credentials

- First, it will try to read the `MODEL_IMAGE_API_KEY` or `ARK_API_KEY` environment variables.
- If not configured, it will try to use `VOLCENGINE_ACCESS_KEY` and `VOLCENGINE_SECRET_KEY` to get the Ark API Key.

## Output Format

- The console will output the generated image URL.
- If the call fails, it will print the error information.

## Examples

```bash
python scripts/image_generate.py "a cute cat"
```
