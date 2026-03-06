# Doubao Skill V2 - Shell 脚本实现

Doubao AI Generation - 文本生图、图片编辑和文本生视频（纯 Shell 版本）

## 版本信息

**版本**: 1.0.0  
**类型**: Shell Script  
**作者**: wenkangwei  
**最后更新**: 2026-03-02

## 功能特性

✅ **文本生图** (Text-to-Image) - 使用 Doubao Seedream 模型  
✅ **图片编辑** (Image Editing) - 去除水印、智能编辑  
✅ **文本生视频** (Text-to-Video) - 使用 Doubao Seedance 模型  
✅ **异步/同步模式** - 支持异步和同步视频生成  
✅ **任务状态查询** - 实时查询生成进度  
✅ **自动文件下载** - 自动保存到 `data/` 目录  
✅ **纯 Shell 实现** - 无 Python 依赖，轻量级

## 目录结构

```
doubao-skill-v2/
├── SKILL.md                    # 技能主文档
├── README.md                   # 本文件 - 快速开始
├── doubao-skill-v2.json       # 技能配置清单
├── CHANGELOG.md                # 更新日志
├── requirements.txt             # 依赖列表
├── references/                 # 参考文档目录
│   ├── README.md              # 快速开始指南
│   └── INTEGRATION_GUIDE.md  # 集成指南
└── scripts/                   # 执行脚本目录
    ├── doubao.sh              # 主脚本（Shell 实现）
    ├── doubao_skill.sh        # Skill 包装器
    └── examples.sh            # 使用示例
```

## 快速开始

### 1. 前置条件

- Bash 4.0+
- curl（HTTP 客户端）
- jq（JSON 处理，可选但推荐）

### 2. 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get install curl jq

# macOS
brew install curl jq

# CentOS/RHEL
sudo yum install curl jq
```

### 3. 设置环境变量

```bash
# 设置 API Key
export ARK_API_KEY="your_api_key_here"

# 或添加到 ~/.bashrc
echo 'export ARK_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc

# 验证
echo $ARK_API_KEY
```

### 4. 验证安装

```bash
cd ~/.openclaw/workspace/skills/doubao-skill-v2/scripts

# 设置执行权限
chmod +x doubao.sh doubao_skill.sh examples.sh

# 显示帮助
./doubao.sh help
```

## 使用方法

### 方式 1: 直接使用 Shell 脚本

```bash
cd scripts

# 生成图片
./doubao.sh img "一只可爱的小猫"

# 编辑图片（去除水印）
./doubao.sh edit "https://..." "remove watermark"

# 生成视频（异步）
./doubao.sh vid "一个人在跳舞" async

# 生成视频（同步）
./doubao.sh vid "一个人在跳舞" sync

# 检查任务状态
./doubao.sh status "task_xxxxx"
```

### 方式 2: 使用 Skill 包装器

```bash
cd scripts

# 通过 Skill 包装器调用
./doubao_skill.sh img "一只可爱的小猫"

# 编辑图片
./doubao_skill.sh edit "https://..." "remove watermark"

# 生成视频
./doubao_skill.sh vid "一个人在跳舞" sync

# 查询状态
./doubao_skill.sh status "task_xxxxx"
```

### 方式 3: 批量处理

```bash
cd scripts

# 批量生成图片
for prompt in "猫" "狗" "鸟"; do
    ./doubao.sh img "一只可爱的${prompt}"
done

# 批量生成视频
for prompt in "跳舞" "唱歌" "画画"; do
    ./doubao.sh vid "一个人在${prompt}" async
done
```

## 技术架构

### 脚本组成

```
doubao.sh           # 主脚本
├─ API 调用逻辑
├─ 文件下载功能
├─ JSON 解析（jq）
└─ 错误处理

doubao_skill.sh     # Skill 包装器
├─ 参数验证
├─ 命令路由
└─ 响应格式化
```

### 数据流

```
用户输入 → Shell 脚本 → API 调用 → JSON 响应 → 文件下载 → 本地存储
```

## 文件管理

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

## API 参考

### Action: img (文生图)

**参数:**
- `prompt` (string, required): 生成提示词

**返回:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "local_path": "data/img_YYYYMMDD_HHMMSS.jpeg",
  "filename": "img_YYYYMMDD_HHMMSS.jpeg"
}
```

**示例:**
```bash
./doubao.sh img "一只可爱的小猫"
```

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
  "filename": "edit_YYYYMMDD_HHMMSS.jpeg",
  "prompt": "remove watermark, keep main content"
}
```

**示例:**
```bash
# 使用默认提示词去除水印
./doubao.sh edit "https://example.com/image.png"

# 自定义编辑提示词
./doubao.sh edit "https://example.com/image.png" "remove logo and watermark, preserve main subject"
```

### Action: vid (文生视频)

**参数:**
- `prompt` (string, required): 生成提示词
- `sync_mode` (string, optional): "sync" 或 "async" (默认: async)
- `image_url` (string, optional): 参考图片 URL（可选）

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
  "filename": "vid_YYYYMMDD_HHMMSS.mp4",
  "prompt": "一个人在跳舞",
  "mode": "sync"
}
```

**示例:**
```bash
# 异步模式（快速返回任务ID）
./doubao.sh vid "一个人在现代城市中跳舞，夜景" async

# 同步模式（等待完成）
./doubao.sh vid "一条龙在云彩中飞舞，奇幻场景" sync
```

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

## 常见问题

### 问题 1: ARK_API_KEY 环境变量未设置

**错误信息:**
```
错误：请先在环境变量 ARK_API_KEY 中设置你的 API Key。
```

**解决方案:**

```bash
# 方式 1: 直接设置
export ARK_API_KEY="your_api_key_here"

# 方式 2: 从配置文件 source
source ~/.basic

# 方式 3: 添加到 ~/.bashrc
echo 'export ARK_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc

# 验证
echo $ARK_API_KEY
```

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
# 复制视频 URL 在浏览器中打开下载
```

### 问题 5: 权限拒绝 (Permission denied)

**错误信息:**
```
bash: ./doubao.sh: Permission denied
```

**解决方案:**

```bash
# 添加执行权限
cd scripts
chmod +x doubao.sh doubao_skill.sh examples.sh
```

## 性能指标

| 操作 | 预期耗时 | 说明 |
|------|---------|------|
| 文生图 | 10-30 秒 | 取决于图片大小和服务器负载 |
| 图片编辑 | 10-30 秒 | 取决于编辑复杂度 |
| 文生视频（启动） | 1-5 秒 | 异步模式返回任务ID |
| 文生视频（完成） | 1-3 分钟 | 同步模式等待完成 |
| 状态查询 | < 1 秒 | 实时查询任务状态 |

## 版本历史

### v1.0.0 (2026-03-02)

✅ **初始版本**
- ✅ Shell 脚本实现
- ✅ 文生图功能
- ✅ 图片编辑功能
- ✅ 文生视频功能（异步 + 同步）
- ✅ 任务状态查询
- ✅ 自动文件下载
- ✅ 符合 OpenClaw/ClawHub 标准

## 技术支持

### 获取帮助

```bash
# 查看帮助信息
cd scripts
./doubao.sh help

# 查看示例
./examples.sh
```

### 查看文档

```bash
# 查看详细文档
cat ../references/SKILL.md

# 查看集成指南
cat ../references/INTEGRATION_GUIDE.md

# 查看更新日志
cat ../CHANGELOG.md
```

### 问题反馈

如遇到问题，请提供以下信息：

1. 系统环境：`uname -a`
2. Shell 版本：`bash --version`
3. 错误信息：完整错误输出
4. 环境变量：`env | grep ARK_API_KEY`

## 开发指南

### 扩展功能

要扩展 doubao-skill-v2 的功能：

1. 在 `scripts/doubao.sh` 中添加新的函数
2. 在 `main()` 中添加新的命令处理
3. 更新 `SKILL.md` 和 `doubao-skill-v2.json`

### 贡献指南

欢迎提交 Pull Request 和 Issue。

---

**版本**: 1.0.0  
**最后更新**: 2026-03-02  
**维护者**: wenkangwei
