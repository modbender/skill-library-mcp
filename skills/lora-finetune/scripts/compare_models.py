#!/usr/bin/env python3
"""Generate base vs fine-tuned comparison images."""
import torch, os
from diffusers import StableDiffusionPipeline
from PIL import Image

prompts = [
    "sndmntls style, children book illustration, watercolor style, a small fox sitting under a glowing mushroom in a moonlit forest",
    "sndmntls style, children book illustration, watercolor style, a friendly whale made of clouds floating above a sleeping village",
    "sndmntls style, children book illustration, watercolor style, a kitten discovering a garden of glowing flowers at night",
]

model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"
lora_path = "./lora_weights"
out_dir = "./comparisons"
os.makedirs(out_dir, exist_ok=True)

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Device: {device}")

# Base model
print("Loading base model...")
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
pipe.to(device)

for i, prompt in enumerate(prompts):
    print(f"[{i+1}/3] Base: generating...")
    img = pipe(prompt, num_inference_steps=30, guidance_scale=7.5, generator=torch.manual_seed(42)).images[0]
    img.save(f"{out_dir}/base_{i+1}.png")
    print(f"  Saved base_{i+1}.png")

# Load LoRA
print("\nLoading LoRA weights...")
pipe.load_lora_weights(lora_path)

for i, prompt in enumerate(prompts):
    print(f"[{i+1}/3] LoRA: generating...")
    img = pipe(prompt, num_inference_steps=30, guidance_scale=7.5, generator=torch.manual_seed(42)).images[0]
    img.save(f"{out_dir}/lora_{i+1}.png")
    print(f"  Saved lora_{i+1}.png")

# Side-by-side
print("\nCreating side-by-side comparisons...")
for i in range(3):
    base = Image.open(f"{out_dir}/base_{i+1}.png")
    lora = Image.open(f"{out_dir}/lora_{i+1}.png")
    combined = Image.new('RGB', (base.width * 2 + 20, base.height + 40), (30, 30, 30))
    combined.paste(base, (0, 40))
    combined.paste(lora, (base.width + 20, 40))
    combined.save(f"{out_dir}/compare_{i+1}.png")
    print(f"  Saved compare_{i+1}.png")

print("\n✅ Done! Comparisons at ./comparisons/")
