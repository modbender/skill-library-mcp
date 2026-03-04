# HF Daily Papers (OpenClaw Skill) — OFR 定制版

从 Hugging Face Daily Papers 热榜筛选 OFR 相关论文，按 6 大领域分类推送。

## 领域分类

| 领域 | 关键词示例 |
|------|----------|
| 🎬 Restoration & Enhancement | restoration, denoising, super-resolution, scratch, flicker, colorization |
| 🎞️ Video & Temporal | video, temporal, optical flow, frame interpolation, propagation |
| ⚡ Efficient Architecture | efficient, pruning, quantization, distillation, real-time |
| 🔭 Vision Backbone & Attention | transformer, attention, mamba, SSM, deformable, swin |
| 🌊 Frequency & Wavelet | wavelet, frequency, fourier, FFT, DWT, subband |
| 🎨 Diffusion & Generative Prior | diffusion, GAN, generative, flow matching, autoregressive |

## 输出

- Markdown: `recommendations/YYYY-MM-DD.md`
- Telegram: `recommendations/YYYY-MM-DD.telegram.txt`（`--telegram` flag）

## CLI

```bash
cd /workspace/openclaw/skills/hf-daily-papers
python3 generator.py              # 仅 Markdown
python3 generator.py --telegram   # Markdown + Telegram 格式
```

## 代理

默认使用 `http://127.0.0.1:7890`（Clash）。可通过环境变量覆盖：

```bash
export HF_DAILY_PAPERS_PROXY=http://127.0.0.1:7897
```

## Cron 配置

- Job ID: `04db7928-d6c1-4b7d-aa9c-5bc1d399b58c`
- 时间: 每天 08:00 上海时间
- 推送: Telegram

## 来源

https://github.com/henry-y/openclaw-paper-tools
