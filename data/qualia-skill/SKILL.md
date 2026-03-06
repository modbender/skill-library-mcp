---
name: qualia
description: Train Robotic AI Models using Qualia. Use when asked to train a robot model, check training status, manage Qualia projects, browse available model types, or inspect datasets.
metadata: {"clawdis":{"emoji":"🤖","requires":{"env":["QUALIA_API_KEY"]}}}
---

# Qualia

Fine-tune and iterate on robotic foundation models — VLAs, reward models, and more — on cloud GPUs.

## Setup

```bash
export QUALIA_API_KEY="your-api-key"
```

## Quick Commands

```bash
# Account
{baseDir}/scripts/qualia.sh credits               # Check credit balance
{baseDir}/scripts/qualia.sh instances             # GPU options and pricing

# Models & data
{baseDir}/scripts/qualia.sh models                             # VLA types and camera slot requirements
{baseDir}/scripts/qualia.sh dataset-keys <huggingface/dataset> # Image keys for camera mapping

# Projects
{baseDir}/scripts/qualia.sh projects                       # List your projects
{baseDir}/scripts/qualia.sh project-create "My Project"   # Create a project
{baseDir}/scripts/qualia.sh project-delete <project_id>   # Delete a project

# Training
{baseDir}/scripts/qualia.sh hyperparams <vla_type> [model_id]  # Default hyperparams (model_id required for smolvla/pi0/pi05)
{baseDir}/scripts/qualia.sh finetune <project_id> <vla_type> <dataset_id> <hours> '<camera_json>'
{baseDir}/scripts/qualia.sh status <job_id>                # Training progress and phase history
{baseDir}/scripts/qualia.sh cancel <job_id>                # Stop a running job
```

## Launching a Fine-Tune Job

### 1. Pick a model

```bash
{baseDir}/scripts/qualia.sh models
```

Supported VLA types: `act`, `smolvla`, `pi0`, `pi05`, `gr00t_n1_5`, `sarm`

### 2. Check your dataset's image keys

```bash
{baseDir}/scripts/qualia.sh dataset-keys your-org/your-dataset
```

### 3. Map image keys to camera slots

Each VLA type has required camera slot names (shown in `models`). Build a JSON mapping:

```json
{"image_0": "front", "image_1": "wrist"}
```

### 4. Create a project (if needed)

```bash
{baseDir}/scripts/qualia.sh project-create "My Robot"
```

### 5. Launch

```bash
# smolvla/pi0/pi05 require --model
{baseDir}/scripts/qualia.sh finetune \
  <project_id> \
  pi0 \
  your-org/your-dataset \
  4 \
  '{"cam_1": "observation.images.top", "cam_2": "observation.images.wrist"}' \
  --model lerobot/pi0 \
  --name "My training run"

# act and gr00t_n1_5 do NOT take --model
{baseDir}/scripts/qualia.sh finetune \
  <project_id> \
  act \
  your-org/your-dataset \
  2 \
  '{"cam_1": "observation.images.top"}'
```

### RA-BC (Reward-Aware Behavior Cloning)

Use a trained SARM reward model to weight training samples. Supported on smolvla, pi0, pi05.

```bash
{baseDir}/scripts/qualia.sh finetune \
  <project_id> pi0 your-org/your-dataset 4 \
  '{"cam_1": "observation.images.top"}' \
  --model lerobot/pi0 \
  --rabc your-org/sarm-reward-model \
  --rabc-image-key observation.images.top \
  --rabc-head-mode sparse
```

### Advanced: custom hyperparameters

```bash
# 1. Get defaults
{baseDir}/scripts/qualia.sh hyperparams pi0 lerobot/pi0

# 2. Validate your overrides
{baseDir}/scripts/qualia.sh hyperparams-validate pi0 '{"learning_rate": 1e-4}'

# 3. Pass them into the job
{baseDir}/scripts/qualia.sh finetune \
  <project_id> pi0 your-org/your-dataset 4 \
  '{"cam_1": "observation.images.top"}' \
  --model lerobot/pi0 \
  --hyper-spec '{"learning_rate": 1e-4, "num_epochs": 50}'
```

### 6. Monitor

```bash
{baseDir}/scripts/qualia.sh status <job_id>
```

## VLA Types

| Type | Description |
|------|-------------|
| `act` | Action Chunking Transformer — fast, lightweight |
| `smolvla` | SmolVLA — efficient open-source VLA |
| `pi0` | π0 — Physical Intelligence foundation model |
| `pi05` | π0.5 — dexterous manipulation variant |
| `gr00t_n1_5` | GR00T N1.5 — NVIDIA humanoid foundation model |
| `sarm` | SARM — reward model for RA-BC (cam_1 only) |

## RA-BC Support

Models that support Reward-Aware Behavior Cloning: `smolvla`, `pi0`, `pi05`

Train a SARM reward model first (vla_type=sarm), then use it to weight samples during VLA fine-tuning via `--rabc` flags.

## Notes

- Training costs are in **credits** (check balance with `credits`)
- Use `instances` to compare GPU options and hourly credit rates
- `dataset-keys` requires a public HuggingFace dataset ID (e.g. `lerobot/aloha_sim_insertion_human`)
- Jobs move through phases: queuing → credit_validation → instance_booting → instance_activation → instance_setup → dataset_preprocessing → training_running → model_uploading → completed
- Terminal states: completed, failed, cancelled
