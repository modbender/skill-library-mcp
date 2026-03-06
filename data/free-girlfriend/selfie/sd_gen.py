#!/usr/bin/env python3
# 免费 Stable Diffusion 图片生成
import sys
import torch
from diffusers import StableDiffusionPipeline

def generate_image(prompt, output_path="output.png"):
    """使用 Stable Diffusion 生成图片"""
    
    print("🔄 加载模型中...")
    
    # 使用较小的模型
    model_id = "runwayml/stable-diffusion-v1-5"
    
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # Mac 用 float32
        use_safetensors=True
    )
    
    # Mac MPS 加速（如果可用）
    if torch.backends.mps.is_available():
        pipe = pipe.to("mps")
        print("✅ 使用 MPS (Apple Silicon) 加速")
    else:
        pipe = pipe.to("cpu")
        print("⚠️  使用 CPU（较慢）")
    
    print(f"🎨 生成图片: {prompt}")
    
    image = pipe(
        prompt,
        num_inference_steps=30,
        guidance_scale=7.5
    ).images[0]
    
    image.save(output_path)
    print(f"✅ 图片已保存: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 sd_gen.py <prompt> [output.png]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output.png"
    
    generate_image(prompt, output)
