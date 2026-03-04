#!/usr/bin/env python3
"""
LoRA fine-tuning for FLUX.1-schnell on Apple Silicon M4 24GB.
Uses memory-efficient loading: text encoders stay on CPU, only transformer on MPS.
"""

import argparse, os, json, gc, time
import torch
from pathlib import Path
from PIL import Image
from datetime import datetime

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default="./training_data")
    p.add_argument("--output_dir", default="./lora_weights")
    p.add_argument("--model_id", default="black-forest-labs/FLUX.1-schnell")
    p.add_argument("--steps", type=int, default=500)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--resolution", type=int, default=512)
    p.add_argument("--log_every", type=int, default=25)
    return p.parse_args()

def load_data(data_dir):
    pairs = []
    for img_path in sorted(Path(data_dir).glob("*.png")):
        txt = img_path.with_suffix(".txt")
        if txt.exists():
            pairs.append((str(img_path), txt.read_text().strip()))
    return pairs

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Device: {device}")
    
    pairs = load_data(args.data_dir)
    print(f"Training data: {len(pairs)} image-caption pairs")
    
    # Load components separately to manage memory
    print("Loading FLUX components (memory-efficient mode)...")
    
    from diffusers import FluxPipeline
    
    # Load with CPU offload to fit in 24GB
    pipe = FluxPipeline.from_pretrained(
        args.model_id,
        torch_dtype=torch.float32,
    )
    
    # Move only the transformer to MPS, keep text encoders on CPU
    pipe.text_encoder.to("cpu")
    pipe.text_encoder_2.to("cpu")
    pipe.vae.to("cpu")
    gc.collect()
    
    # Apply LoRA to transformer only
    from peft import LoraConfig, get_peft_model
    
    lora_config = LoraConfig(
        r=args.rank,
        lora_alpha=args.rank,
        target_modules=["to_q", "to_k", "to_v", "to_out.0"],
        lora_dropout=0.05,
    )
    
    pipe.transformer = get_peft_model(pipe.transformer, lora_config)
    pipe.transformer.to(device)
    pipe.transformer.print_trainable_parameters()
    
    # Optimizer — only trainable LoRA params
    trainable = [p for p in pipe.transformer.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.01)
    
    log = {"config": vars(args), "losses": [], "start_time": datetime.now().isoformat()}
    
    print(f"\n🚀 Training: {args.steps} steps, rank={args.rank}, lr={args.lr}")
    start = time.time()
    
    for step in range(1, args.steps + 1):
        img_path, caption = pairs[(step - 1) % len(pairs)]
        
        # Load + resize image
        image = Image.open(img_path).convert("RGB").resize((args.resolution, args.resolution))
        img_tensor = torch.tensor(list(image.getdata()), dtype=torch.float32)
        img_tensor = img_tensor.reshape(1, args.resolution, args.resolution, 3).permute(0, 3, 1, 2) / 255.0
        img_tensor = (img_tensor * 2.0 - 1.0).to("cpu")
        
        # Encode image on CPU (VAE stays on CPU)
        with torch.no_grad():
            latents = pipe.vae.encode(img_tensor).latent_dist.sample()
            latents = (latents * pipe.vae.config.scaling_factor).to(device)
        
        # Encode text on CPU
        with torch.no_grad():
            prompt_embeds, pooled_prompt_embeds, text_ids = pipe.encode_prompt(
                prompt=caption, prompt_2=caption,
            )
            prompt_embeds = prompt_embeds.to(device)
            pooled_prompt_embeds = pooled_prompt_embeds.to(device)
            text_ids = text_ids.to(device)
        
        # Noise + timestep on MPS
        noise = torch.randn_like(latents)
        t = torch.randint(0, 1000, (1,), device=device).float()
        noisy = latents + noise * (t / 1000.0)
        
        # img_ids
        h, w = latents.shape[2], latents.shape[3]
        img_ids = torch.zeros(1, h * w, 3, device=device)
        
        # Forward through LoRA-wrapped transformer on MPS
        pred = pipe.transformer(
            hidden_states=noisy,
            timestep=t,
            encoder_hidden_states=prompt_embeds,
            pooled_projections=pooled_prompt_embeds,
            txt_ids=text_ids,
            img_ids=img_ids,
        ).sample
        
        loss = torch.nn.functional.mse_loss(pred, noise)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        loss_val = loss.item()
        log["losses"].append({"step": step, "loss": loss_val})
        
        if step % args.log_every == 0 or step == 1:
            elapsed = time.time() - start
            eta = elapsed / step * (args.steps - step)
            print(f"  Step {step}/{args.steps} | Loss: {loss_val:.6f} | ETA: {eta/60:.0f}min")
    
    # Save
    print(f"\n💾 Saving LoRA weights...")
    pipe.transformer.save_pretrained(args.output_dir)
    
    log["end_time"] = datetime.now().isoformat()
    log["final_loss"] = log["losses"][-1]["loss"]
    log["total_time_seconds"] = time.time() - start
    with open(os.path.join(args.output_dir, "training_log.json"), "w") as f:
        json.dump(log, f, indent=2)
    
    print(f"✅ Done! {args.steps} steps in {log['total_time_seconds']/60:.1f}min")
    print(f"   Final loss: {log['final_loss']:.6f}")
    print(f"   Weights: {args.output_dir}")

if __name__ == "__main__":
    main()
