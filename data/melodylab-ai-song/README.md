# ZeeLin Song Generator 🎵

**用一句话创作完整歌曲** - 由 AI 驱动的音乐创作工具

[![Version](https://img.shields.io/badge/version-1.0.4-blue.svg)](https://clawhub.ai/skills/melodylab-ai-song)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange.svg)](https://openclaw.ai)

## ✨ 功能特性

### 🤖 AI 全自动模式（新功能！）
让 AI 随机为你创作惊喜歌曲：
- 自动选择主题、风格、情绪
- 完全随机，给你意想不到的创意
- 适合寻求灵感或探索新风格

### 🎨 自定义创作模式
完全控制你的音乐：
- 自定义主题和故事
- 选择音乐风格（流行/摇滚/民谣/电子等）
- 设定情绪基调（甜蜜/悲伤/激昂/平静等）
- 决定人声或纯音乐

### 🎼 生成流程
1. **Gemini AI** 生成高质量歌词
2. **可编辑确认** - 修改直到满意
3. **Suno AI** 一次性生成 2 首完整歌曲
4. **多版本选择** - 选择你最喜欢的版本

## 🚀 快速开始

### 安装

```bash
# 使用 ClawHub CLI
clawhub install melodylab-ai-song

# 或者手动克隆
git clone https://github.com/yourusername/melodylab-ai-song.git ~/.openclaw/workspace/skills/melodylab-ai-song
```

### 使用示例

**AI 全自动模式**:
```
你: 帮我生成一首歌
AI: [询问模式选择]
你: 全自动
AI: [自动创作]
```

**自定义创作**:
```
你: 写一首关于夏天海边初恋的流行歌，要甜蜜的感觉
AI: [生成歌词并等待确认]
你: 确认
AI: [生成音乐并返回两个版本]
```

## 📋 技术架构

```
用户输入
   ↓
ZeeLin Song Generator (OpenClaw Skill)
   ↓
MelodyLab API (https://melodylab.top)
   ↓
┌─────────────┬─────────────┐
│  Gemini AI  │   Suno AI   │
│  (歌词生成)  │  (音乐合成)  │
└─────────────┴─────────────┘
   ↓
返回 2 首完整歌曲 + 封面
```

## 🔒 隐私与安全

### 我们承诺

- ✅ **不存储用户输入** - 创意描述仅用于实时生成
- ✅ **HTTPS 加密传输** - 所有数据通过 TLS 1.2+ 加密
- ✅ **最小化数据收集** - 仅收集必要的创作参数
- ✅ **无第三方追踪** - 不使用 Google Analytics 等追踪工具
- ✅ **7 天日志保留** - 仅用于故障排查，之后自动删除

### 第三方服务

本技能使用以下第三方服务：

| 服务 | 用途 | 隐私政策 |
|------|------|----------|
| **Google Gemini** | 歌词生成 | [查看政策](https://ai.google.dev/gemini-api/terms) |
| **Suno AI** | 音乐合成 | [查看政策](https://suno.com/terms) |
| **MelodyLab** | API 聚合 | [查看 PRIVACY.md](./PRIVACY.md) |

详细隐私说明请查看 [PRIVACY.md](./PRIVACY.md)

## ⚠️ 使用限制

### 速率限制
- 每用户每分钟最多 10 个请求
- 生成时间：歌词 30-90 秒，音乐 60-180 秒

### 内容限制
禁止生成以下内容：
- ❌ 仇恨言论或歧视性内容
- ❌ 暴力或威胁性内容
- ❌ 色情或露骨内容
- ❌ 侵犯版权的内容

违规请求会被自动过滤并可能导致 IP 封禁。

## 🎯 支持的风格

### 音乐风格
流行 Pop | 摇滚 Rock | 民谣 Folk | 电子 Electronic | 说唱 Hip-hop | 古风 Ancient Style | 爵士 Jazz | R&B | 乡村 Country | 金属 Metal | 朋克 Punk | 布鲁斯 Blues | 雷鬼 Reggae | 拉丁 Latin

### 情绪基调
甜蜜 Sweet | 悲伤 Sad | 激昂 Passionate | 平静 Calm | 怀旧 Nostalgic | 欢快 Cheerful | 深沉 Deep | 浪漫 Romantic | 治愈 Healing | 振奋 Uplifting | 忧郁 Melancholic | 神秘 Mysterious

## 🛠️ 故障排查

### 常见错误

**403 用户已被封禁**
- 原因：API 配额耗尽或账户限制
- 解决：稍后重试或联系开发者

**429 Too Many Requests**
- 原因：请求频率过高
- 解决：等待 60 秒后重试

**500 Internal Server Error**
- 原因：后端服务异常
- 解决：稍后重试

**timeout**
- 原因：生成超时（超过 2 分钟）
- 解决：重新提交请求

## 📊 版本历史

### v1.0.4 (2026-03-04)
- ✨ 新增 AI 全自动创作模式
- 📝 完善隐私政策和安全说明
- 🔒 添加详细的数据处理透明度信息
- 📚 优化文档和使用示例

### v1.0.3 (2026-03-04)
- 🏷️ 更新技能名称为 "ZeeLin Song Generator"

### v1.0.2 (2026-03-03)
- 🐛 修复 API 调用问题
- 📝 改进文档

### v1.0.1 (2026-03-03)
- 🎉 初始版本发布

## 🤝 贡献

欢迎提交问题和建议！

- **Issues**: [ClawHub 技能页面](https://clawhub.ai/skills/melodylab-ai-song)
- **Email**: 通过项目主页联系
- **讨论**: OpenClaw Discord 社区

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 👤 作者

**刘东江** (@lidngjing317853)

- 项目主页: https://melodylab.top
- ClawHub: [@dongjiangliu9-tech](https://clawhub.ai/users/dongjiangliu9-tech)

## 🙏 致谢

感谢以下服务提供商：
- [Google Gemini](https://ai.google.dev/) - 强大的歌词生成能力
- [Suno AI](https://suno.com/) - 高质量的音乐合成技术
- [OpenClaw](https://openclaw.ai/) - 优秀的 AI 代理平台

---

**免责声明**: 本技能生成的音乐内容版权归属请遵守 Suno AI 的许可协议。不得用于商业用途，除非获得相应授权。
