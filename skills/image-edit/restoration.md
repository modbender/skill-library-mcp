# Image Restoration

Fix damaged, blurry, or degraded images with AI.

## Face Restoration

### GFPGAN

```bash
pip install gfpgan

# CLI
python inference_gfpgan.py -i inputs/ -o results/ -v 1.4 -s 2
```

```python
from gfpgan import GFPGANer

restorer = GFPGANer(
    model_path="GFPGANv1.4.pth",
    upscale=2,
    arch="clean",
    channel_multiplier=2
)

_, _, output = restorer.enhance(
    input_img,
    has_aligned=False,
    only_center_face=False,
    paste_back=True
)
```

### CodeFormer

```python
from codeformer import CodeFormer

model = CodeFormer()
result = model.restore(
    image,
    fidelity=0.5  # 0=quality, 1=fidelity to original
)
```

**Fidelity slider:**
- Low (0.1-0.3) — more enhancement, may change face
- High (0.7-0.9) — preserves original, less enhancement

### Replicate

```python
import replicate

output = replicate.run(
    "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3",
    input={"img": open("face.jpg", "rb"), "scale": 2}
)
```

## Old Photo Restoration

### Bringing Old Photos Back to Life

```python
import replicate

output = replicate.run(
    "microsoft/bringing-old-photos-back-to-life:c75db81db6cbd809d93b27b0f3e88a4c88aec3ed9be33b8c0f7f0c98d14f1d34",
    input={
        "image": open("old_photo.jpg", "rb"),
        "with_scratch": True
    }
)
```

**Features:**
- Scratch removal
- Face restoration
- Color enhancement

## Denoising

### Real-ESRGAN Denoise

```python
from realesrgan import RealESRGAN

model = RealESRGAN(device, scale=1)  # scale=1 for denoise only
model.load_weights("realesr-general-x4v3.pth")
```

### OpenCV Denoising

```python
import cv2

# For color images
denoised = cv2.fastNlMeansDenoisingColored(
    image,
    None,
    h=10,           # Filter strength
    hForColorComponents=10,
    templateWindowSize=7,
    searchWindowSize=21
)
```

## Colorization

### DeOldify

```python
from deoldify import device
from deoldify.visualize import get_image_colorizer

colorizer = get_image_colorizer(artistic=True)
result = colorizer.get_transformed_image(
    "bw_photo.jpg",
    render_factor=35
)
```

### Replicate

```python
output = replicate.run(
    "arielreplicate/deoldify_image:0da600fab0c45a66211339f1c16b71345d22f26ef5fea3dca1bb90bb5711e950",
    input={"input_image": open("bw.jpg", "rb")}
)
```

## Restoration Pipeline

1. **Remove scratches/damage** — Old Photos model
2. **Denoise** — if grainy
3. **Restore faces** — GFPGAN/CodeFormer
4. **Colorize** — if B&W
5. **Upscale** — to final resolution
6. **Sharpen** — light enhancement

## Quality Tips

- **Preserve original** — always keep unedited copy
- **Gradual enhancement** — don't over-process
- **Check faces** — restoration can change features
- **Manual touchup** — AI may miss spots
- **Add grain** — restored images can look too clean
