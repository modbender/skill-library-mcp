# Network Volumes

Persistent storage for large models. Download once, reuse forever.

## Why Use Volumes?

| Without | With |
|---------|------|
| Download 50GB model every session | Download once |
| 15-30 min startup | 1-2 min startup |
| Lose checkpoints on preemption | Checkpoints persist |

## CLI Commands

```bash
gpu volume list                    # List all volumes
gpu volume list --detailed         # With usage info
gpu volume create --name my-vol --size 200 --datacenter US-OR-1
gpu volume set-global vol_xxx      # Set as default
gpu volume status                  # Check current volume
gpu volume extend vol_xxx --size 300
gpu volume delete vol_xxx
```

## Volume Modes

```jsonc
// Global (default) - shared across projects
{ "volume_mode": "global" }

// Dedicated - project-specific volume
{ "volume_mode": "dedicated", "dedicated_volume_id": "vol_xxx" }

// None - ephemeral storage only
{ "volume_mode": "none" }

// Explicit volume ID
{ "network_volume_id": "vol_xxx" }
```

## Download Strategies

Pre-download models to volume:

```jsonc
{
  "download": [
    // HuggingFace
    { "strategy": "hf", "source": "black-forest-labs/FLUX.1-dev" },

    // Civitai (model ID or AIR URN)
    { "strategy": "civitai", "source": "4384" },

    // Git repo (auto-updates when clean)
    { "strategy": "git", "source": "https://github.com/comfyanonymous/ComfyUI", "target": "ComfyUI" },

    // HTTP direct
    { "strategy": "http", "source": "https://example.com/model.bin", "target": "models/model.bin" }
  ]
}
```

| Strategy | Use Case |
|----------|----------|
| `hf` | HuggingFace models |
| `civitai` | Civitai models |
| `git` | Tool repos (ComfyUI, etc.) |
| `git-lfs` | Repos with large files |
| `http` | Direct URL downloads |
| `script` | Custom shell script |

## Mount Location

Volumes mount at `/runpod-volume/`:

```
/runpod-volume/
├── huggingface/      # HF cache (auto-configured)
├── models/           # Custom models
└── checkpoints/      # Training saves
```

## Sizing Guide

| Use Case | Size |
|----------|------|
| ComfyUI (SDXL + LoRAs) | 100GB |
| Video gen (Wan, Hunyuan) | 200GB |
| LLM (70B) | 150GB |
| Multi-workflow | 500GB |

**Pricing:** ~$0.15/GB/month (100GB = ~$15/mo)

## Best Practices

1. **One volume per project type** - Don't mix image/video/LLM models
2. **Use download spec** - Pre-download in gpu.jsonc, not at runtime
3. **Save checkpoints to volume** - `/runpod-volume/checkpoints/`
4. **Match datacenter to GPU** - Volume and pod must be same region

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Volume not mounting | Check volume ID, same datacenter as pod |
| No space left | Delete unused models, extend volume |
| Slow file access | Write to local SSD, copy to volume at end |
| Pod won't start | Datacenter full - try different region or GPU |
