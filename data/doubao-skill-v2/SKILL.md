---
name: doubao-image-video-skill-v2
version: 1.0.0
description: "Doubao (Volcengine ARK) API Shell 脚本实现 - 文本生图、图片编辑和文本生视频,接口文档https://www.volcengine.com/docs/82379/1520757?lang=zh#y2hhTyHB"
author: "wenkangwei"
tags: ["image", "video", "shell"]
---

### 目录结构

```
doubao-skill-v2/
├── SKILL.md                    # 技能主文档（本文件）
├── README.md                   # 技能说明
├── doubao-skill-v2.json       # 技能配置清单
├── CHANGELOG.md                # 更新日志
├── requirements.txt             # 依赖（curl, jq）
├── references/                 # 参考文档目录
│   ├── README.md              # 快速开始指南
│   ├── SKILL.md              # 详细技能文档
│   └── INTEGRATION_GUIDE.md  # 集成指南
└── scripts/                   # 执行脚本目录
    ├── doubao.sh              # 主脚本（shell实现）
    ├── doubao_skill.sh        # Skill包装脚本
    └── examples.sh            # 使用示例
```

---

## 🚀 快速开始

### 前置条件

- Bash 4.0+
- curl（HTTP客户端）
- jq（JSON处理，可选）
- ARK_API_KEY (从 https://console.volcengine.com/ark 获取)

### 安装步骤

```bash
# 1. 进入 skill 目录
cd ~/.openclaw/workspace/skills/doubao-skill-v2

# 2. 安装依赖
sudo apt-get install curl jq  # Ubuntu/Debian
# 或
brew install curl jq  # macOS

# 3. 设置环境变量
export ARK_API_KEY="your_api_key_here"

# 或添加到 ~/.bashrc
echo 'export ARK_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc

# 4. 验证安装
cd scripts
./doubao.sh help
```

---

## 📚 使用方法

### 使用建议
1. 优先使用方法1
2. 视频生成任务优先使用同步方法,避免浪费token到监控步骤

### 方式 1(优先使用): Shell 脚本直接调用

```bash
cd ~/.openclaw/workspace/skills/doubao-skill-v2/scripts

# 生成图片
./doubao.sh img "一只可爱的小猫"

# 编辑图片（去除水印）
./doubao.sh edit "https://..." "remove watermark"

# 生成视频（异步）
./doubao.sh vid "一个人在跳舞" async ''

# 生成视频（同步 - 等待完成）
./doubao.sh vid "一个人在跳舞" sync ''

# 检查任务状态
./doubao.sh status "task_xxxxx"
```


---

## 📖 API 参考

### Action: img (文生图)

**参数:**
- `prompt` (string, required): 生成提示词

**返回:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "local_path": "data/img_YYYYMMDD_HHMMSS.jpeg",
  "prompt": "一只可爱的小猫"
}
```

**示例:**
```bash
./doubao.sh img "一只可爱的小猫"
```

---

### Action: edit (图片编辑)

**参数:**
- `image_url` (string, required): 要编辑的图片 URL
- `prompt` (string, optional): 编辑提示词（默认: "remove watermark, keep main content"）

**返回:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "local_path": "data/edit_YYYYMMDD_HHMMSS.jpeg",
  "prompt": "remove watermark, keep main content"
}
```

**功能说明:**
- 使用 AI 智能去除图片水印
- 保持图片主要内容不被裁剪
- 支持自定义编辑提示词
- 基于 Image-to-Image 技术重新生成图片

**示例:**
```bash
# 使用默认提示词去除水印
./doubao.sh edit "https://example.com/image.png"

# 自定义编辑提示词
./doubao.sh edit "https://example.com/image.png" "remove logo and watermark, preserve main subject"
```

---

### Action: vid (文生视频)

**参数:**
- `prompt` (string, required): 生成提示词
- `sync_mode` (string, optional): "sync" 或 "async" (默认: async)
- `image_url` (string, optional): 参考图片 URL

**返回 (async 模式):**
```json
{
  "status": "success",
  "task_id": "task_xxxxx",
  "prompt": "一个人在跳舞"
}
```

**返回 (sync 模式):**
```json
{
  "status": "success",
  "task_id": "task_xxxxx",
  "video_url": "https://...",
  "local_path": "data/vid_YYYYMMDD_HHMMSS.mp4",
  "prompt": "一个人在跳舞"
}
```

**示例:**
```bash
# 异步模式（快速返回任务ID）
./doubao.sh vid "一个人在跳舞" async

# 同步模式（等待完成）
./doubao.sh vid "一个人在跳舞" sync ''
```

---

### Action: status (检查任务状态)

**参数:**
- `task_id` (string, required): 任务 ID

**返回:**
```json
{
  "status": "running",
  "progress": 50,
  "task_id": "task_xxxxx"
}
```

**状态值:**
- `pending`: 任务已提交，等待处理
- `running`: 任务正在处理中
- `succeeded`: 任务成功完成
- `failed`: 任务失败

**示例:**
```bash
./doubao.sh status "task_xxxxx"
```

---

## 🎯 技术特性

### Shell 脚本实现

✅ **纯 Bash 脚本**
- 无 Python 依赖
- 轻量级，易于部署
- 适合嵌入式环境

✅ **自动化处理**
- 自动下载文件到 `data/` 目录
- 时间戳文件名
- 错误处理和重试

✅ **异步/同步模式**
- 视频：异步返回 task_id，同步等待完成
- 自动轮询检查状态
- 最大轮询次数限制

---

## 📊 性能指标

| 操作 | 预期耗时 | 说明 |
|------|---------|------|
| 文生图 | 10-30 秒 | 取决于图片大小和服务器负载 |
| 图片编辑 | 10-30 秒 | 取决于编辑复杂度 |
| 文生视频（启动） | 1-5 秒 | 异步模式返回任务ID |
| 文生视频（完成） | 1-3 分钟 | 同步模式等待完成 |
| 状态查询 | < 1 秒 | 实时查询任务状态 |

---

## 🐛 故障排除

### 问题 1: ARK_API_KEY 环境变量未设置

**错误信息:**
```
错误：请先在环境变量 ARK_API_KEY 中设置你的 API Key。
```

**解决方案:**

```bash
# 方式 1: 直接设置
export ARK_API_KEY="your_api_key_here"

# 方式 2: 添加到 ~/.bashrc
echo 'export ARK_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc

# 验证
echo $ARK_API_KEY
```

---

### 问题 2: jq 命令未找到

**错误信息:**
```
jq: command not found
```

**解决方案:**

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# CentOS/RHEL
sudo yum install jq
```

---

### 问题 3: curl 命令未找到

**错误信息:**
```
curl: command not found
```

**解决方案:**

```bash
# Ubuntu/Debian
sudo apt-get install curl

# macOS
brew install curl

# CentOS/RHEL
sudo yum install curl
```

---

### 问题 4: 视频下载失败 (403 Forbidden)

**错误信息:**
```
⚠️  警告：视频 URL 下载失败 (403 Forbidden)
原因：视频 URL 有访问限制，可能需要浏览器环境
```

**解决方案:**

视频 URL 有时效性签名和访问限制，无法直接通过 curl 下载。

```bash
# 使用浏览器手动下载视频
# 复制视频 URL 到浏览器中打开
```

---

## 🧪 测试示例

### 测试 1: 基础文生图

```bash
cd ~/.openclaw/workspace/skills/doubao-skill-v2/scripts

# 设置环境变量
export ARK_API_KEY="your_api_key"

# 运行测试
./doubao.sh img "一只可爱的小猫"
```

**预期结果:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "local_path": "data/img_20260302_012345.jpeg",
  "prompt": "一只可爱的小猫"
}
```

---

### 测试 2: 图片编辑（去除水印）

```bash
cd scripts

# 使用默认提示词去除水印
./doubao.sh edit "https://example.com/image.png"

# 自定义编辑提示词
./doubao.sh edit "https://example.com/image.png" "remove logo and watermark, preserve main subject"
```

**预期结果:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "local_path": "data/edit_20260302_012345.jpeg",
  "prompt": "remove watermark, keep main content"
}
```

---

### 测试 3: 异步文生视频

```bash
cd scripts

# 启动视频生成
./doubao.sh vid "一个人在现代城市中跳舞，夜景" async

# 记录返回的 task_id

# 检查状态
./doubao.sh status "task_xxxxx"
```

**预期结果 (第一步):**
```json
{
  "status": "success",
  "task_id": "task_xxxxx",
  "prompt": "一个人在现代城市中跳舞，夜景"
}
```

**预期结果 (检查状态):**
```json
{
  "status": "running",
  "progress": 50,
  "task_id": "task_xxxxx"
}
```

---

### 测试 4: 同步文生视频

```bash
cd scripts

# 这会等待视频生成完成（可能需要 1-3 分钟）
./doubao.sh vid "一条龙在云彩中飞舞，奇幻场景" sync ''
```

**预期结果:**
```json
{
  "status": "success",
  "task_id": "task_xxxxx",
  "video_url": "https://...",
  "local_path": "data/vid_20260302_012345.mp4",
  "prompt": "一条龙在云彩中飞舞，奇幻场景"
}
```

---

## 📝 依赖说明

### 必需依赖

- **curl**: HTTP 客户端，用于 API 调用
- **bash**: 4.0+，脚本执行环境

### 可选依赖

- **jq**: JSON 处理工具，用于解析 API 响应

### 安装命令

```bash
# Ubuntu/Debian
sudo apt-get install curl jq

# macOS
brew install curl jq

# CentOS/RHEL
sudo yum install curl jq
```

---

## 🔄 工作流程

### 图片生成流程

```
用户输入 → 调用 doubao.sh img → 调用 API → 解析响应 → 下载图片 → 保存到 data/ → 返回本地路径
```

### 图片编辑流程

```
用户提供图片 URL → 调用 doubao.sh edit → 调用 API → 解析响应 → 下载编辑后的图片 → 保存到 data/ → 返回本地路径
```

### 视频生成流程（异步）

```
用户输入 → 调用 doubao.sh vid async → 调用 API → 获取 task_id → 返回 task_id
```

### 视频生成流程（同步）

```
用户输入 → 调用 doubao.sh vid sync → 调用 API → 获取 task_id → 循环检查状态 → 完成后下载 → 保存到 data/ → 返回本地路径
```

---

## 📁 文件管理

### data 目录

所有生成的文件自动保存到 `data/` 目录：

```
data/
├── img_YYYYMMDD_HHMMSS.jpeg     # 生成的图片
├── edit_YYYYMMDD_HHMMSS.jpeg   # 编辑后的图片
└── vid_YYYYMMDD_HHMMSS.mp4     # 生成的视频
```

### 文件命名规则

- 图片：`img_YYYYMMDD_HHMMSS.jpeg`
- 编辑图片：`edit_YYYYMMDD_HHMMSS.jpeg`
- 视频：`vid_YYYYMMDD_HHMMSS.mp4`

---

## 📈 版本历史

### v1.0.0 (2026-03-02)

✅ 初始版本
- ✅ Shell 脚本实现
- ✅ 文生图功能
- ✅ 图片编辑功能
- ✅ 文生视频功能（异步 + 同步）
- ✅ 任务状态查询
- ✅ 自动文件下载
- ✅ 符合 OpenClaw/ClawHub 标准

---

## 🆘 获取帮助

### 查看帮助信息

```bash
cd scripts
./doubao.sh help
```

### 查看示例

```bash
cd scripts
./examples.sh
```

### 查看文档

```bash
# 查看详细文档
cat ../references/SKILL.md

# 查看集成指南
cat ../references/INTEGRATION_GUIDE.md

# 查看快速开始
cat ../references/README.md
```

---

## 🔐 安全性最佳实践

### 不要硬编码 API Key

```bash
# ❌ 错误
API_KEY="sk-xxxxx"

# ✅ 正确
export ARK_API_KEY="your_api_key"
```

### 使用环境变量文件

```bash
# ~/.bashrc
export ARK_API_KEY="your_api_key"
```

### 保护 API Key

- 不要将 API Key 提交到版本控制系统
- 使用环境变量存储敏感信息
- 定期轮换 API Key

---

## 📚 参考资源

- [Volcengine ARK 官方文档](https://www.volcengine.com/docs/82379)
- [Doubao API 文档](https://console.volcengine.com/ark)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [Bash 脚本编程指南](https://tldp.org/LDP/Bash/Bash-Prompt-HOWTO.html)

---

**版本**: 1.0.0
**最后更新**: 2026-03-02
**维护者**: wenkangwei
