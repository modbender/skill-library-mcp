# PrintPal API Reference

## Quality Levels

| Quality | Resolution | Credits | Est. Time | Texture Support |
|---------|-----------|---------|-----------|-----------------|
| default | 256 cubed | 4 | 20 sec | No |
| high | 384 cubed | 6 | 30 sec | No |
| ultra | 512 cubed | 8 | 60 sec | No |
| **super** | 768 cubed | 20 | 3 min | No |
| super_texture | 768 cubed | 40 | 6 min | Yes |
| superplus | 1024 cubed | 30 | 4 min | No |
| superplus_texture | 1024 cubed | 50 | 12 min | Yes |

## Output Formats

| Format | Extension | Description | Availability |
|--------|-----------|-------------|--------------|
| **STL** | .stl | 3D printing format | All quality levels |
| GLB | .glb | Binary glTF (web/games) | All quality levels |
| OBJ | .obj | Wavefront OBJ | All quality levels |
| PLY | .ply | Polygon file format | default, high, ultra |
| FBX | .fbx | Autodesk FBX | super, superplus only |

**Note**: Texture generation (super_texture, superplus_texture) only supports GLB and OBJ formats.

## API Key

Get your API key from: https://printpal.io/api-keys

Set environment variable:
```bash
export PRINTPAL_API_KEY="pp_live_your_api_key_here"
```

## Rate Limits

- 50 requests per minute per API key
- 10,000 requests per day per account
- 5 concurrent generations maximum

## Pricing

Purchase credits at: https://printpal.io/buy-credits

---

# WaveSpeed API Reference

## Model: google/nano-banana/text-to-image

Text-to-image generation model used for creating images from text prompts.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| prompt | string | required | The text prompt for generation |
| aspect_ratio | string | 1:1 | Options: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| output_format | string | png | Options: png, jpeg |
| enable_sync_mode | boolean | false | Wait for result before returning |
| enable_base64_output | boolean | false | Return base64 instead of URL |

### API Key

Get your API key from: https://wavespeed.ai/accesskey

Set environment variable:
```bash
export WAVESPEED_API_KEY="your_api_key_here"
```

### Usage

```python
import wavespeed

output = wavespeed.run(
    "google/nano-banana/text-to-image",
    {
        "enable_base64_output": False,
        "enable_sync_mode": True,
        "output_format": "png",
        "prompt": "your prompt here"
    }
)

image_url = output["outputs"][0]
```
