# gpu.jsonc Configuration

Full schema: `https://gpu-cli.sh/schema/v1/gpu.json`

## Minimal Config

```jsonc
{
  "$schema": "https://gpu-cli.sh/schema/v1/gpu.json",
  "project_id": "my-project",
  "gpu_types": [{ "type": "RTX 4090" }],
  "outputs": ["results/"]
}
```

## All Fields

### GPU Selection

```jsonc
{
  // Priority list - tries in order
  "gpu_types": [
    { "type": "RTX 4090" },
    { "type": "RTX A6000" },
    { "type": "A100 PCIe 80GB", "count": 2 }
  ],

  // Constraints
  "min_vram": 24,              // Minimum VRAM in GB
  "max_price": 1.50,           // Max $/hour
  "regions": ["US-TX-1"],      // Allowed regions
  "cloud_type": "secure"       // "secure" or "community"
}
```

### Output Sync

```jsonc
{
  // Patterns to sync FROM pod (real-time)
  "outputs": ["results/", "models/*.pt", "generated/**/*.png"],

  // Patterns to exclude
  "exclude_outputs": ["*.tmp", "*.log"],

  // Sync from absolute paths on pod
  "extra_outputs": [
    { "remote": "/tmp/cache", "local": "cache/" }
  ]
}
```

### Model Downloads

```jsonc
{
  "download": [
    // HuggingFace
    { "strategy": "hf", "source": "black-forest-labs/FLUX.1-dev", "allow": "*.safetensors" },

    // Git repo
    { "strategy": "git", "source": "https://github.com/comfyanonymous/ComfyUI", "target": "ComfyUI" },

    // HTTP file
    { "strategy": "http", "source": "https://example.com/model.bin", "target": "models/model.bin" },

    // Civitai
    { "strategy": "civitai", "source": "4384" }
  ]
}
```

### Ports & Networking

```jsonc
{
  // Simple ports
  "ports": [8000, 8188],

  // With activity tracking
  "ports": [
    { "port": 8188, "http": { "activity_paths": ["/prompt"] } }
  ],

  // Keep proxy alive after pod stops (auto-resume)
  "persistent_proxy": true,

  // Paths that don't reset idle timer
  "health_check_paths": ["/health", "/ready"]
}
```

### Pod Lifecycle

```jsonc
{
  // Auto-stop after X minutes idle (default: 5)
  "keep_alive_minutes": 10,

  // Resume timeout
  "resume_timeout_secs": 180
}
```

### Environment Setup

```jsonc
{
  "environment": {
    // Base Docker image
    "base_image": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",

    // System packages
    "system": {
      "apt": [{ "name": "ffmpeg" }, { "name": "git" }]
    },

    // Python dependencies
    "python": {
      "requirements": "requirements.txt"
    },

    // Shell commands
    "shell": {
      "steps": [{ "run": "pip install -U pip" }]
    }
  }
}
```

### Lifecycle Hooks

```jsonc
{
  "hooks": {
    // Wait for service ready
    "readiness": {
      "type": "command",
      "command": "curl -f http://localhost:8000/health",
      "retry_count": 5,
      "timeout_secs": 30
    },

    // Run before pod stops
    "shutdown": {
      "type": "script",
      "script": "save_checkpoint.py",
      "timeout_secs": 60
    }
  }
}
```

### Storage

```jsonc
{
  // Storage mode
  "storage_mode": "network",        // "built-in", "network", "managed"
  "network_volume_id": "vol_xxx",   // Persistent volume
  "workspace_size_gb": 100          // Built-in volume size
}
```

### Templates (for sharing)

```jsonc
{
  "template": {
    "name": "My Template",
    "description": "Does XYZ",
    "author": "me"
  },
  "startup": "python main.py --listen 0.0.0.0",
  "inputs": [
    { "type": "select", "name": "model", "options": ["A", "B"] }
  ]
}
```

## Known GPU Types

```
RTX 3070, RTX 3080, RTX 3090
RTX 4070 Ti, RTX 4080, RTX 4090
RTX A4000, RTX A5000, RTX A6000
RTX 2000 Ada, RTX 4000 Ada, RTX 5000 Ada, RTX 6000 Ada
T4, L4, L40, L40S
A100 PCIe 40GB, A100 PCIe 80GB, A100 SXM 80GB
H100 PCIe, H100 SXM, H100 NVL
H200, H200 NVL, B200
MI300X
```
