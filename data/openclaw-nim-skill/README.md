# OpenClaw NVIDIA NIM Skill

🚀 **Token-Saving Superpower for OpenClaw/Claude Code**

This skill integrates the **NVIDIA NIM (Inference Microservices)** platform into your OpenClaw environment. It allows you to "outsource" heavy tasks like summarization, long-form explanation, or deep reasoning to specialized models (GLM-5, Kimi-k2.5, DeepSeek R1, etc.) for FREE, saving up to 90%+ of your main agent's context tokens.

## 🌟 Features

- **Multi-Model Support**: Switch between top Chinese and Global models instantly.
- **Zero Dependencies**: Pure Python implementation using `urllib`.
- **Token Efficiency**: Keeps your main conversation lean by handling long inputs/outputs externally.

## 📦 Installation

1. Clone this repo into your `skills/` directory.
2. Get your free API Key from [NVIDIA Build](https://build.nvidia.com/).
3. Add `export NVIDIA_API_KEY="your-key"` to your `.zshrc` or `.bashrc`.

## 🛠 Usage

In your OpenClaw session:
> "Use /nim with kimi to summarize this long file: [path]"

Or via CLI:
```bash
python3 scripts/nim_call.py kimi "Summarize the history of AI"
```

## 📜 License
MIT
