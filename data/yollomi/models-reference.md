# Yollomi API – Models Reference

## Unified Endpoint

`POST /api/v1/generate` with `type`, `modelId`, and model-specific params.

List models: `GET /api/v1/models`

## Aspect Ratio (aspectRatio)

Common aspect ratios for text-to-image models:

- **1:1** - Square (default)
- **16:9** - Landscape
- **9:16** - Portrait

## Image Models (type: "image")

| modelId | Credits | Required | Optional |
|---------|---------|----------|----------|
| flux | 4 × numOutputs | prompt | aspectRatio (1:1, 16:9, 9:16), outputFormat, numOutputs |
| flux-schnell | 2 × numOutputs | prompt | aspectRatio, outputFormat, numOutputs |
| flux-2-pro | 15 × numOutputs | prompt | aspectRatio, outputFormat, numOutputs |
| remove-bg | 0 | imageUrl | |
| nano-banana | 4 | prompt | imageUrl, aspectRatio, outputFormat |
| nano-banana-pro | 15 | prompt | imageUrl, aspectRatio, outputFormat |
| flux-kontext-pro | 4 | prompt | imageUrl, aspectRatio, outputFormat |
| z-image-turbo | 1 | prompt | width, height, outputFormat |
| imagen-4-ultra | 6 | prompt | aspectRatio, outputFormat |
| image-4-fast | 3 | prompt | aspectRatio, numOutputs |
| ideogram-v3-turbo | 3 | prompt | aspectRatio, resolution, styleType |
| stable-diffusion-3-5-large | 7 × numOutputs | prompt | aspectRatio, numOutputs |
| seedream-4-5 | 4 | prompt | imageUrl, aspectRatio |
| object-remover | 3 | image, mask | |
| face-swap | 3 | swapImage, inputImage | |
| image-upscaler | 1 | imageUrl | scale (1,2,4,6,8,10), faceEnhance |
| photo-restoration | 4 | imageUrl | |
| qwen-image-edit | 3 | image, prompt | outputFormat, enhancePrompt |
| qwen-image-edit-plus | 3 | image, prompt | outputFormat |
| virtual-try-on | 3 | clothImage, personImage | clothType, outputFormat |
| ai-background-generator | 5 | imageUrl | prompt, outputFormat |

## Video Models (type: "video")

| modelId | Credits | Notes |
|---------|---------|-------|
| openai-sora-2 | ~50+ | seconds, aspect_ratio |
| google-veo-3 | 10 | |
| google-veo-3-fast | 9 | |
| google-veo-3-1 | 10 | |
| google-veo-3-2 | 10 | |
| google-veo-3-1-fast | 9 | |
| kling-2-1 | 9 | |
| kling-v2-6-motion-control | 7/sec | videoDuration, mode |
| minimax-hailuo-2-3 | 9 | |
| minimax-hailuo-2-3-fast | 9 | |
| bytedance-seedance-1-pro-fast | 8 | |
| runway-gen4-turbo | varies | |
| pixverse-5 | 9 | |
| wan-2-5-i2v | 9 | img2vid |
| wan-2-5-t2v | 9 | txt2vid |
| wan-2-6-i2v | 29 | img2vid |
| wan-2-6-t2v | 29 | txt2vid |

Video params go in `inputs`: aspect_ratio, duration/seconds, image, start_image, first_frame_image, etc.
