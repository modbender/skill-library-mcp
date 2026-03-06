---
name: gpu-deploy
description: "在 GPU 服务器上部署 vLLM 模型服务。支持多服务器配置，自动检查 GPU 和端口占用，一键部署流行的开源模型。"
homepage: https://github.com/vllm-project/vllm
metadata: { "openclaw": { "emoji": "🚀", "requires": { "bins": ["ssh"] } } }
---

# 🚀 GPU 部署技能

在 GPU 服务器上快速部署 vLLM 模型服务。

## ✨ 功能特点

- 🖥️ **多服务器支持** - 配置多个 GPU 服务器，灵活选择
- 🔍 **自动检查** - 一键检查 GPU 状态和端口占用
- 🤖 **模型库** - 预置流行模型配置
- ⚡ **快速部署** - 简单命令即可启动服务

---

## 📋 快速开始

### 1. 配置服务器

创建 `~/.config/gpu-deploy/servers.json`：

```json
{
  "servers": {
    "gpu1": {
      "host": "gpu1",
      "user": "lnsoft",
      "gpu_count": 4,
      "model_path": "/data/models/llm"
    },
    "my-gpu": {
      "host": "192.168.1.100",
      "user": "ubuntu",
      "gpu_count": 2,
      "model_path": "/home/ubuntu/models"
    }
  },
  "default_server": "gpu1"
}
```

### 2. 检查服务器状态

```bash
# 使用默认服务器
gpu-deploy check

# 指定服务器
gpu-deploy check --server gpu1
```

### 3. 部署模型

```bash
# 部署预设模型
gpu-deploy deploy deepseek-r1-32b

# 指定端口
gpu-deploy deploy deepseek-r1-32b --port 8112
```

---

## 🎛️ 可用命令

### `check` - 检查服务器状态

检查 GPU 显存和端口占用情况。

```bash
gpu-deploy check [--server NAME] [--port PORT]
```

**输出示例：**
```
✅ GPU 状态正常
- 4 × Tesla T4 (15GB)
- 显存占用: 12.6GB/卡
- 温度: 51-55°C

✅ 端口 8111 可用
```

### `deploy` - 部署模型

启动 vLLM 模型服务。

```bash
gpu-deploy deploy <MODEL_NAME> [--server NAME] [--port PORT]
```

**支持的模型：**
- `deepseek-r1-32b` - DeepSeek-R1-Distill-Qwen-32B-AWQ
- `llama-3-8b` - Llama 3 8B
- `qwen-7b` - Qwen 7B
- `mistral-7b` - Mistral 7B

### `list` - 列出可用模型

```bash
gpu-deploy list
```

### `ps` - 查看运行中的服务

```bash
gpu-deploy ps [--server NAME]
```

### `stop` - 停止服务

```bash
gpu-deploy stop [--server NAME] [--port PORT]
```

---

## 🔧 手动使用（无脚本）

如果不想用封装脚本，也可以直接用原始命令：

### 检查 GPU

```bash
ssh <user>@<host> nvidia-smi
```

### 检查端口

```bash
ssh <user>@<host> "lsof -i :<port> 2>/dev/null || echo '端口可用'"
```

### 部署模型（DeepSeek R1 32B）

```bash
ssh <user>@<host> "tmux new-session -d -s vllm '
source /data/miniconda3/etc/profile.d/conda.sh && \
conda activate vllm && \
cd /data/models/llm && \
vllm serve /data/models/llm/deepseek/DeepSeek-R1-Distill-Qwen-32B-AWQ/ \
  --tensor-parallel-size 4 \
  --max-model-len 102400 \
  --dtype half \
  --port 8111 \
  --served-model-name gpt-4o-mini
'"
```

---

## 📦 添加自定义模型

在 `~/.config/gpu-deploy/models.json` 中添加：

```json
{
  "my-model": {
    "name": "My Awesome Model",
    "path": "/path/to/model",
    "tensor_parallel_size": 2,
    "max_model_len": 8192,
    "dtype": "half",
    "port": 8111,
    "served_model_name": "my-model"
  }
}
```

---

## ⚠️ 注意事项

1. **部署前检查** - 总是先运行 `check` 确认资源可用
2. **后台运行** - 建议使用 tmux/screen 保持服务运行
3. **端口管理** - 不同模型使用不同端口
4. **显存估算** - 7B 模型约需 8-10GB，32B 约需 10-14GB/卡

---

## 🔗 相关链接

- vLLM 文档: https://docs.vllm.ai
- 模型下载: https://huggingface.co/models
- 问题反馈: https://github.com/your-username/gpu-deploy-skill

---

**由 OpenClaw 社区贡献 🦞**
