# 常见问题 FAQ

## 安装问题

### Q1: pip install 报错 "externally-managed-environment"
```bash
# 使用 --break-system-packages 标志
pip3 install edge-tts --break-system-packages
```

### Q2: Stable Diffusion 下载模型很慢
- 使用镜像加速（HuggingFace 镜像）
- 或手动下载模型文件放到 `~/.cache/huggingface/`

### Q3: Mac Intel 芯片运行很慢
- 建议使用 Apple Silicon（M 系列）
- Intel Mac 会回退到 CPU，速度较慢

## 使用问题

### Q4: 生成的图片不像同一个人
这是 Stable Diffusion 的正常现象。要生成一致的角色需要：
- 使用 LoRA 微调模型
- 或使用 IP-Adapter 固定人脸
- 或参考 Clawra 的方案（使用固定参考图 + 图片编辑）

### Q5: 视频没有嘴型同步
当前是简化版（图片+音频合成）。完整的嘴型同步需要：
1. 安装完整 Wav2Lip
2. 下载预训练模型
3. 运行推理流程

详见 SKILL.md 的进阶配置部分。

### Q6: 语音音色不满意
Edge TTS 支持多种音色：
```bash
# 查看所有中文女声
edge-tts --list-voices | grep "zh-CN.*Female"

# 使用不同音色
./voice/tts.sh "文本" out.mp3 zh-CN-XiaoyiNeural
```

## 性能问题

### Q7: 图片生成太慢
优化方案：
- 减少推理步数（默认 30，可降到 20）
- 使用更小的模型
- 确保启用 MPS 加速（M 芯片）

### Q8: 内存不足
- 减少 batch size
- 使用 float16 精度（需修改代码）
- 关闭其他应用释放内存

## 功能问题

### Q9: 能不能实现 Live2D 动画？
可以！需要额外集成：
- VTube Studio
- 或自己开发 Live2D SDK 集成

计划在未来版本添加。

### Q10: 支持其他语言吗？
Edge TTS 支持多语言：
```bash
edge-tts --list-voices | grep English
```

Stable Diffusion 支持英文 prompt。

## 开源问题

### Q11: 可以商用吗？
MIT 许可证允许商用，但：
- Stable Diffusion 模型有各自的许可证
- 请遵守各组件的开源协议

### Q12: 如何贡献代码？
参见 CONTRIBUTING.md

---

有其他问题？提交 [Issue](../../issues) 或加入 OpenClaw 社区讨论！
