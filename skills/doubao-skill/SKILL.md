---
name: doubao-image-video-skill
version: 1.0.0           
description: "ByteDance/Doubao (Volcengine ARK) API 进行文本生图、图片编辑和文本生视频的操作"
author: "wenkangwei"
tags: ["image", "video"]
---

### 目录结构

```
doubao-skill/
├── SKILL.md                    # 技能主文档（本文件）
├── README.md                   # 技能说明
├── doubao-skill.json           # 技能配置清单
├── CHANGELOG.md                # 更新日志
├── requirements.txt             # Python 依赖
├── references/                 # 参考文档目录
│   ├── README.md              # 快速开始指南
│   ├── SKILL.md              # 详细技能文档
│   └── INTEGRATION_GUIDE.md  # 集成指南
└── scripts/                   # 执行脚本目录
    ├── cli.py                # CLI 命令行工具
    ├── doubao_demo.py         # API 客户端
    ├── doubao_skill.py        # 核心 Skill 实现
    └── doubao_skill_examples.py  # 使用示例
```

---

## 🚀 快速开始

### 前置条件

- Python 3.7+
- ARK_API_KEY (从 https://console.volcengine.com/ark 获取)

### 安装步骤

```bash
# 1. 进入 skill 目录
cd ~/.openclaw/workspace/skills/doubao-skill

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 设置环境变量
export ARK_API_KEY="your_api_key_here"

# 或 source 配置文件
source ~/.basic  # 如果有此文件

# 4. 验证安装（进入 scripts 目录）
cd scripts
python3 cli.py help
```

---

## 📚 使用方法

### 方式 1: CLI 命令行工具

```bash
cd ~/.openclaw/workspace/skills/doubao-skill/scripts

# 生成图片
python3 cli.py img "一只可爱的小猫"

# 编辑图片（去除水印）
python3 cli.py edit "https://..." "remove watermark"

# 生成视频（异步）
python3 cli.py vid "一个人在跳舞" async

# 生成视频（同步 - 等待完成）
python3 cli.py vid "一个人在跳舞" sync

# 检查任务状态
python3 cli.py status "task_xxxxx"
```

### 方式 2: Python 脚本调用

```python
import asyncio
import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, '/home/wwk/.openclaw/workspace/skills/doubao-skill/scripts')

from doubao_skill import handler

async def main():
    # 设置 API Key
    os.environ["ARK_API_KEY"] = "your_api_key"

    # 生成图片
    result = await handler({
        "action": "img",
        "prompt": "一只可爱的小猫"
    })

    print(result)

asyncio.run(main())
```

### 方式 3: 直接使用 DoubaoDemo API

```python
import asyncio
import sys
import os
import subprocess

# 设置环境变量
os.environ["ARK_API_KEY"] = "your_api_key"

async def generate_image(prompt):
    """生成图片"""
    cmd = [
        "python3",
        "/home/wwk/.openclaw/workspace/skills/doubao-skill/scripts/doubao_demo.py",

async def generate_image(prompt):
    """生成图片"""
    cmd = [
        "python3",
        "/home/wwk/.openclaw/workspace/skills/doubao-skill/doubao_demo.py",
        "img",
        prompt
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Error: {stderr.decode()}")
        return None

    import json
    return json.loads(stdout.decode())

asyncio.run(generate_image("一只可爱的小猫"))
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
  "prompt": "一只可爱的小猫"
}
```

**示例:**
```bash
python3 cli.py img "一只可爱的小猫"
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
  "prompt": "remove watermark, keep main content"
}
```

**功能说明:**
- 使用 AI 智能去除图片水印
- 保持图片主要内容不被裁剪
- 支持自定义编辑提示词
- 基于 Image-to-Image 技术重新生成图片

**注意事项:**
- 需要有效的 ARK API Key
- 某些编辑模型可能需要特定权限
- 建议使用描述性提示词以获得最佳效果

**示例:**
```bash
# 使用默认提示词去除水印
python3 cli.py edit "https://example.com/image.png"

# 自定义编辑提示词
python3 cli.py edit "https://example.com/image.png" "remove logo and watermark, preserve main subject"
```

**提示词建议:**
- "remove watermark, keep main content" - 温和去除水印
- "remove logo and text, preserve background" - 去除Logo和文字
- "clean image, remove overlays" - 清理图片，去除覆盖层
- "keep subject, remove text" - 保留主体，去除文字

---

### Action: vid (文生视频)

**参数:**
- `prompt` (string, required): 生成提示词
- `sync_mode` (string, optional): "sync" 或 "async" (默认: async)

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
  "result_url": "https://...",
  "prompt": "一个人在跳舞"
}
```

**示例:**
```bash
# 异步模式（快速返回任务ID）
cd scripts
python3 cli.py vid "一个人在跳舞" async

# 同步模式（等待完成）
python3 cli.py vid "一个人在跳舞" sync
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
python3 cli.py status "task_xxxxx"
```

---

## 🐛 常见问题与解决方案

### 问题 1: ARK_API_KEY 环境变量未设置

**错误信息:**
```
ValueError: ARK_API_KEY 环境变量未设置
```

**解决方案:**

```bash
# 方式 1: 直接设置
export ARK_API_KEY="your_api_key_here"

# 方式 2: 从配置文件 source
source ~/.basic

# 验证
echo $ARK_API_KEY
```

---

### 问题 2: python 命令未找到

**错误信息:**
```
/bin/bash: line 1: python: command not found
```

**解决方案:**

```bash
# 使用 python3 代替 python
python3 cli.py img "测试提示词"
```

**原因:** 系统上 Python 命名为 `python3` 而不是 `python`

---

### 问题 3: 依赖包未安装

**错误信息:**
```
ModuleNotFoundError: No module named 'requests'
```

**解决方案:**

```bash
cd ~/.openclaw/workspace/skills/doubao-skill
pip install -r requirements.txt

# 或手动安装
pip install requests aiohttp pydantic pytimeparse
```

---

### 问题 4: doubao_demo.py 文件缺失

**错误信息:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'doubao_demo.py'
```

**解决方案:**

doubao_demo.py 已经创建在 `/home/wwk/.openclaw/workspace/skills/doubao-skill/doubao_demo.py`

如果仍然报错，检查文件是否存在：

```bash
ls -la ~/.openclaw/workspace/skills/doubao-skill/doubao_demo.py
```

---

### 问题 5: API 请求失败 (401 Unauthorized)

**错误信息:**
```
API Error: 401 - Unauthorized
```

**解决方案:**

```bash
# 1. 验证 API Key 是否正确
echo $ARK_API_KEY

# 2. 检查 API Key 格式（应该以类似 "ark-" 开头）

# 3. 重新设置 API Key
export ARK_API_KEY="correct_api_key"
```

---

### 问题 6: API 请求失败 (400 Bad Request)

**错误信息:**
```
API Error: 400 - Bad Request
```

**解决方案:**

```bash
# 1. 检查提示词是否为空或格式不正确

# 2. 尝试简单的提示词测试
python3 cli.py img "test"

# 3. 检查网络连接
curl -I https://ark.cn-beijing.volces.com/
```

---

### 问题 7: 视频生成超时

**错误信息:**
```
Request timeout (10 minutes exceeded)
```

**解决方案:**

视频生成通常需要 1-3 分钟，这是正常现象。

```bash
# 使用异步模式，避免超时
python3 cli.py vid "提示词" async

# 然后定期检查状态
python3 cli.py status "task_xxxxx"
```

---

### 问题 8: 图片编辑效果不理想

**现象:**
编辑后的图片水印仍然存在或内容改变太大

**解决方案:**

```bash
# 调整 strength 参数（在代码中修改）
# 0.3 = 温和编辑（推荐用于去水印）
# 0.5 = 中等编辑
# 0.7 = 激进编辑

# 尝试不同的提示词
python3 cli.py edit "https://..." "keep main subject, clean background"
python3 cli.py edit "https://..." "remove only overlay text, preserve image"
```

---

## 🧪 测试示例

### 测试 1: 基础文生图

```bash
cd ~/.openclaw/workspace/skills/doubao-skill/scripts

# 设置环境变量
export ARK_API_KEY="your_api_key"

# 运行测试
python3 cli.py img "一只可爱的小猫"
```

**预期结果:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "prompt": "一只可爱的小猫"
}
```

---

### 测试 2: 图片编辑（去除水印）

```bash
cd scripts

# 使用默认提示词去除水印
python3 cli.py edit "https://example.com/image.png"

# 自定义编辑提示词
python3 cli.py edit "https://example.com/image.png" "remove logo and watermark, preserve main subject"
```

**预期结果:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "prompt": "remove watermark, keep main content"
}
```

---

### 测试 3: 异步文生视频

```bash
cd scripts

# 启动视频生成
python3 cli.py vid "一个人在现代城市中跳舞，夜景" async

# 记录返回的 task_id

# 检查状态
python3 cli.py status "task_xxxxx"
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
python3 cli.py vid "一条龙在云彩中飞舞，奇幻场景" sync
```

**预期结果:**
```json
{
  "status": "success",
  "result_url": "https://...",
  "prompt": "一条龙在云彩中飞舞，奇幻场景"
}
```

---

## 📊 性能指标

| 操作 | 预期耗时 | 说明 |
|------|---------|------|
| 文生图 | 10-30 秒 | 取决于图片大小和服务器负载 |
| 文生视频（启动） | 1-5 秒 | 异步模式返回任务ID |
| 文生视频（完成） | 1-3 分钟 | 同步模式等待完成 |
| 状态查询 | < 1 秒 | 实时查询任务状态 |
| 并发支持 | 支持 | 可同时处理多个请求 |

---

## 🔧 配置与自定义

### 修改超时时间

编辑 `doubao_skill.py` 文件：

```python
async def _run_python_script(self, *args) -> Dict[str, Any]:
    # ...
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=600  # 修改为所需秒数（默认 600 秒 = 10 分钟）
    )
    # ...
```

### 修改图片尺寸

编辑 `doubao_demo.py` 文件：

```python
def generate_image(self, prompt):
    # ...
    json={
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"  # 修改为所需尺寸
    },
    # ...
```

---

## 📝 开发与扩展

### 添加新的 Action

1. 在 `doubao_skill.py` 的 `execute()` 方法中添加新的 action 类型
2. 创建对应的处理方法
3. 更新 `doubao-skill.json` 中的 capabilities 和 parameters
4. 在 `cli.py` 中添加 CLI 命令

---

## 🆘 获取帮助

### 查看帮助信息

```bash
cd ~/.openclaw/workspace/skills/doubao-skill

# CLI 帮助
python3 cli.py help

# 运行示例
python3 doubao_skill_examples.py
```

### 查看文档

- `README.md` - 快速开始指南
- `INTEGRATION_GUIDE.md` - 集成指南
- `doubao_skill_examples.py` - 代码示例

---

## 🔐 安全性最佳实践

### 不要硬编码 API Key

```python
# ❌ 错误
ARK_API_KEY = "sk-xxxxx"

# ✅ 正确
import os
ARK_API_KEY = os.getenv("ARK_API_KEY")
```

### 使用环境变量文件

```bash
# ~/.basic
export ARK_API_KEY="your_api_key"

# 使用时 source
source ~/.basic
```

### 保护 API Key

- 不要将 API Key 提交到版本控制系统
- 使用环境变量存储敏感信息
- 定期轮换 API Key

---

## 📌 注意事项

1. **API Key 保密**: 不要在公开场合分享 ARK_API_KEY
2. **费用控制**: 注意 API 调用量，避免意外超支
3. **错误处理**: 始终检查返回的 `status` 字段
4. **超时处理**: 视频生成可能耗时较长，建议使用异步模式
5. **网络稳定**: 确保网络连接稳定，避免请求中断

---

## 📚 相关资源

- [Volcengine ARK 官方文档](https://www.volcengine.com/docs/82379)
- [Doubao API 文档](https://console.volcengine.com/ark)
- [OpenClaw 文档](https://docs.openclaw.ai)

---

**最后更新**: 2026-03-01
**维护者**: Doubao Skill Team
