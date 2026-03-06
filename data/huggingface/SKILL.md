---
name: huggingface
description: Manage models, datasets, Spaces, and repositories using Hugging Face CLI (hf). Supports authentication, upload, download, Space creation, and more.
metadata: {"openclaw":{"emoji":"🤗","requires":{"bins":["hf"],"env":["HF_TOKEN"]}}}
---

# Hugging Face CLI Skill

Use Hugging Face Hub CLI (`hf`) for various operations.

## Environment Variables

- `HF_TOKEN`: Hugging Face API Token (get from https://huggingface.co/settings/tokens)

## Core Features

### 1. Authentication Management (`hf auth`)

```bash
# Check login status
hf auth whoami

# List all tokens
hf auth list

# Login
hf auth login

# Logout
hf auth logout

# Switch token
hf auth switch
```

### 2. Model Management (`hf models`)

```bash
# List models (supports sorting and filtering)
hf models ls --sort downloads --limit 10
hf models ls --search "llama"

# Get model info
hf models info meta-llama/Llama-3.2-1B-Instruct
```

### 3. Dataset Management (`hf datasets`)

```bash
# List datasets
hf datasets ls --limit 10
hf datasets ls --search "imagenet"

# Get dataset info
hf datasets info HuggingFaceFW/fineweb
```

### 4. Spaces Management (`hf spaces`)

```bash
# List Spaces
hf spaces ls --limit 10

# Get Space info
hf spaces info username/repo-name

# Hot-reload (experimental, for Gradio 6.1+)
hf spaces hot-reload username/repo-name app.py
hf spaces hot-reload username/repo-name -f ./local/app.py
```

### 5. Repository Management (`hf repos`)

```bash
# Create new repository
hf repos create my-model --type model
hf repos create my-dataset --type dataset
hf repos create my-space --type space

# Delete repository
hf repos delete username/repo-name

# Set as private
hf repos settings username/repo-name --private

# Manage branches
hf repos branch create username/repo-name feature-branch
hf repos branch delete username/repo-name feature-branch

# Manage tags
hf repos tag create username/repo-name v1.0
hf repos tag delete username/repo-name v1.0

# Move repository to another namespace
hf repos move old-namespace/my-model new-namespace/my-model
```

### 6. Download Files (`hf download`)

```bash
# Download entire model
hf download meta-llama/Llama-3.2-1B-Instruct

# Download specific files
hf download meta-llama/Llama-3.2-1B-Instruct config.json tokenizer.json

# Download with glob patterns
hf download meta-llama/Llama-3.2-1B-Instruct --include "*.safetensors"
hf download meta-llama/Llama-3.2-1B-Instruct --include "*.json" --exclude "*.bin"

# Download to local directory
hf download meta-llama/Llama-3.2-1B-Instruct --local-dir ./models/llama

# Download dataset
hf download HuggingFaceM4/FineVision --repo-type dataset
```

### 7. Upload Files (`hf upload`)

```bash
# Upload entire directory
hf upload my-cool-model . .

# Upload single file
hf upload username/my-model ./models/model.safetensors

# Upload to dataset
hf upload username/my-dataset ./data /train --repo-type dataset

# With commit message
hf upload username/my-model ./models . --commit-message="Epoch 34/50" --commit-description="Val accuracy: 68%"

# Create Pull Request
hf upload bigcode/the-stack . . --repo-type dataset --create-pr

# Create private repository
hf upload username/my-private-model . . --private
```

### 8. Collection Management (`hf collections`)

```bash
# Create collection
hf collections create "My Models"

# Add item to collection
hf collections add-item username/my-collection moonshotai/kimi-k2 model

# List collections
hf collections ls

# Get collection info
hf collections info username/my-collection

# Update collection
hf collections update username/my-collection --title "New Title"

# Update collection item
hf collections update-item username/my-collection ITEM_OBJECT_ID --note "Updated note"

# Delete item
hf collections delete-item username/my-collection ITEM_OBJECT_ID

# Delete collection
hf collections delete username/my-collection
```

## Usage Examples

### Example 1: Download and Upload Model
```bash
# Download model
hf download meta-llama/Llama-3.2-1B-Instruct --local-dir ./llama-model

# Upload to your repository
hf upload username/my-llama ./llama-model .
```

### Example 2: Manage Space
```bash
# Create Space
hf repos create my-app --type space

# Upload code
hf upload username/my-app ./app.py

# Hot-reload for development
hf spaces hot-reload username/my-app app.py
```

### Example 3: Batch Operations
```bash
# Download all safetensors files
hf download meta-llama/Llama-3.2-1B-Instruct --include "*.safetensors"

# Upload and create PR
hf upload username/model . . --create-pr --commit-message="Update model"
```

## Notes

1. **Token Management**: Ensure `HF_TOKEN` environment variable is set, or use `--token` parameter
2. **Large File Upload**: For large folders, consider using `hf upload-large-folder`
3. **Space Hot-Reload**: Only works with Gradio 6.1+, experimental feature
4. **Free Space Limits**:
   - Free fixed vCPU: 2
   - RAM: 16GB
   - No persistent storage (use external storage or HF Datasets)

## Resources

- [Hugging Face CLI Documentation](https://huggingface.co/docs/huggingface_hub/en/guides/cli)
- [Hugging Face Token Settings](https://huggingface.co/settings/tokens)
- [Hugging Face Spaces](https://huggingface.co/spaces)
