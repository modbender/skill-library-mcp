# AutoClip Pro - 视频批量处理技能包

> 🎬 开箱即用的小白友好视频批量处理工具

## 📖 简介

AutoClip Pro 是一个专为视频创作者设计的批量处理技能包，支持：

- ✂️ **批量剪辑** - 自动裁剪、分割视频
- 📝 **字幕生成** - AI 自动生成字幕
- 🎨 **模板应用** - 知识科普、情感故事、搞笑段子多种风格
- 🔄 **批量渲染** - 一键处理整个视频文件夹

## 🚀 快速开始

### 方式一：一键安装（推荐新手）

双击 `install.bat`，等待安装完成即可。

### 方式二：手动安装

```bash
# 1. 安装依赖
npm install

# 2. 安装 FFmpeg（如果没有）
# Windows: 下载 https://ffmpeg.org/download.html 并添加到 PATH
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### 运行

双击 `run.bat` 或运行：

```bash
node scripts/batch-process.js
```

## 📁 目录结构

```
video-batch-skill/
├── README.md           # 本文件
├── TUTORIAL.md         # 详细教程
├── install.bat         # 一键安装
├── run.bat             # 一键运行
├── config.json         # 配置文件
├── scripts/
│   ├── video-editor.js     # 视频编辑核心
│   └── batch-process.js    # 批量处理入口
├── templates/
│   ├── knowledge.json      # 知识科普模板
│   ├── emotional.json      # 情感故事模板
│   └── funny.json          # 搞笑段子模板
└── examples/
    └── sample-video/       # 示例视频
```

## ⚙️ 配置说明

编辑 `config.json` 自定义处理参数：

```json
{
  "inputDir": "./input",
  "outputDir": "./output",
  "template": "knowledge",
  "resolution": "1080p",
  "fps": 30,
  "addSubtitles": true,
  "addWatermark": false
}
```

## 📚 模板说明

| 模板 | 风格 | 适用场景 |
|------|------|----------|
| knowledge | 知识科普 | 教育视频、知识分享 |
| emotional | 情感故事 | Vlog、情感表达 |
| funny | 搞笑段子 | 娱乐内容、短视频 |

## 🛠️ 系统要求

- Node.js 18+
- FFmpeg 4.0+
- 4GB+ 内存
- Windows 10/11 或 macOS 10.15+

## 📞 支持

遇到问题？查看 [TUTORIAL.md](./TUTORIAL.md) 获取详细帮助。

---

**版本**: V1.0  
**作者**: AI Company 技术团队  
**许可**: MIT License