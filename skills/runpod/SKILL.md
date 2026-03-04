---
name: runpod
description: Manage RunPod GPU cloud instances - create, start, stop, connect to pods via SSH and API. Use when working with RunPod infrastructure, GPU instances, or need SSH access to remote GPU machines. Handles pod lifecycle, SSH proxy connections, filesystem mounting, and API queries. Requires runpodctl (brew install runpod/runpodctl/runpodctl).
---

# RunPod Skill

Manage RunPod GPU cloud instances, SSH connections, and filesystem access.

## Prerequisites

```bash
brew install runpod/runpodctl/runpodctl
runpodctl config --apiKey "your-api-key"
```

**SSH Key:** runpodctl manages SSH keys in `~/.runpod/ssh/`:

```bash
runpodctl ssh add-key
```

View and manage keys at: https://console.runpod.io/user/settings

**Mount script configuration:**
The mount script checks `~/.ssh/runpod_key` first, then falls back to runpodctl's default key. Override with:
```bash
export RUNPOD_SSH_KEY="$HOME/.runpod/ssh/RunPod-Key"
```

Host keys are stored separately in `~/.runpod/ssh/known_hosts` (isolated from your main SSH config). Uses `StrictHostKeyChecking=accept-new` to verify hosts on reconnect while allowing new RunPod instances.

## Quick Reference

```bash
runpodctl get pod                    # List pods
runpodctl get pod <id>               # Get pod details
runpodctl start pod <id>             # Start pod
runpodctl stop pod <id>              # Stop pod
runpodctl ssh connect <id>           # Get SSH command
runpodctl send <file>                # Send file to pod
runpodctl receive <code>             # Receive file from pod
```

## Common Operations

### Create Pod

```bash
# Without volume
runpodctl create pod --name "my-pod" --gpuType "NVIDIA GeForce RTX 4090" --imageName "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404"

# With volume (100GB at /workspace)
runpodctl create pod --name "my-pod" --gpuType "NVIDIA GeForce RTX 4090" --imageName "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404" --volumeSize 100 --volumePath "/workspace"
```

**Important:** When using a volume (`--volumeSize`), always specify `--volumePath` too. Without it:
```
error creating container: ... invalid mount config for type "volume": field Target must not be empty
```

### SSH to Pod

```bash
# Get SSH command
runpodctl ssh connect <pod_id>

# Connect directly (copy command from above)
ssh -p <port> root@<ip> -i ~/.ssh/runpod_key
```

### Mount Pod Filesystem (SSHFS)

```bash
./scripts/mount_pod.sh <pod_id> [base_dir]
```

Mounts pod to `~/pods/<pod_id>` by default.

**Access files:**
```bash
ls ~/pods/<pod_id>/
cat ~/pods/<pod_id>/workspace/my-project/train.py
```

**Unmount:**
```bash
fusermount -u ~/pods/<pod_id>
```

## Helper Script

| Script | Purpose |
|--------|---------|
| `mount_pod.sh` | Mount pod filesystem via SSHFS (no runpodctl equivalent) |

## Web Service Access

Proxy URLs:
```
https://<pod_id>-<port>.proxy.runpod.net
```

Common ports:
- **8188**: ComfyUI
- **7860**: Gradio
- **8888**: Jupyter
- **8080**: Dev tools
