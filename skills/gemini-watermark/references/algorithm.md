# Gemini Watermark Removal Algorithm

## Overview

Gemini AI applies a semi-transparent white star/sparkle logo to generated images using standard alpha compositing. This tool reverses the compositing to recover the original pixel values.

## Alpha Blending Model

### Forward (How Gemini Applies the Watermark)

For each pixel in the watermark region:

```
watermarked[c] = alpha * logo_value + (1 - alpha) * original[c]
```

Where:
- `alpha` is the watermark opacity at that pixel (0.0 = transparent, 1.0 = opaque)
- `logo_value` = 255.0 (white logo)
- `c` is the color channel (R, G, B)

### Reverse (How We Remove It)

Rearranging the equation:

```
original[c] = (watermarked[c] - alpha * logo_value) / (1 - alpha)
```

### Safety Guards

- **Alpha threshold (0.002)**: Pixels with alpha below this are skipped (noise)
- **Max alpha (0.99)**: Alpha is clamped to prevent division by near-zero
- **Pixel clamping [0, 255]**: Results are clamped to valid range

## Alpha Maps

The alpha map represents the watermark's transparency pattern. It is derived from "background captures" - screenshots of the Gemini watermark rendered on a white (255,255,255) background.

### Derivation

```
alpha(x, y) = max(R, G, B) / 255.0
```

Using the max of RGB channels (rather than a single channel) handles any colored logo variants.

### Two Sizes

| Size | Dimensions | Margin | Used When |
|------|-----------|--------|-----------|
| Small | 48x48 | 32px | Either dimension <= 1024 |
| Large | 96x96 | 64px | Both dimensions > 1024 |

### Position

The watermark is always in the bottom-right corner:

```
pos_x = image_width - watermark_size - margin
pos_y = image_height - watermark_size - margin
```

## Three-Stage Detection Algorithm

### Stage 1: Spatial NCC (50% Weight)

Normalized Cross-Correlation between the image region's grayscale brightness and the alpha map:

```
NCC = sum((I - mean_I)(A - mean_A)) / sqrt(sum((I - mean_I)^2) * sum((A - mean_A)^2))
```

If spatial NCC < 0.25 (circuit breaker), the image is rejected early.

### Stage 2: Gradient NCC (30% Weight)

Both the image region and alpha map are processed through 3x3 Sobel edge detectors:

```
Gx = [[-1,0,1],[-2,0,2],[-1,0,1]]
Gy = [[-1,-2,-1],[0,0,0],[1,2,1]]
magnitude = sqrt(Gx^2 + Gy^2)
```

NCC is then computed on the gradient magnitudes, capturing the structural star/sparkle pattern regardless of brightness.

### Stage 3: Variance Analysis (20% Weight)

Compares texture (standard deviation) in the watermark region vs. a reference region directly above:

```
score = clamp(1.0 - stddev(watermark) / stddev(reference), 0.0, 1.0)
```

Watermarks dampen high-frequency texture, so lower variance in the watermark region indicates watermark presence.

### Combined Confidence

```
confidence = 0.50 * spatial + 0.30 * gradient + 0.20 * variance
detected = confidence >= 0.35
```

## References

- [Removing Gemini AI Watermarks: A Deep Dive into Reverse Alpha Blending](https://allenkuo.medium.com/removing-gemini-ai-watermarks-a-deep-dive-into-reverse-alpha-blending-bbbd83af2a3f)
- [GeminiWatermarkTool (C++ reference implementation)](https://github.com/allenk/GeminiWatermarkTool)
