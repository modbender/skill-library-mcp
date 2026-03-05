# Doubao Skill - OpenClaw 集成指南

## 📦 目录结构

OpenClaw/ClawHub 识别的标准目录格式：

```
doubao-skill/
├── SKILL.md                    # 技能主文档（必需）
├── doubao-skill.json           # 技能清单配置（必需）
├── requirements.txt             # 依赖列表
├── references/                 # 参考文档
│   ├── README.md              # 快速开始
│   ├── SKILL.md              # 详细技能文档
│   └── INTEGRATION_GUIDE.md   # 本文件 - 集成指南
└── scripts/                   # 执行脚本
    ├── doubao_skill.py        # 核心 Skill 类
    ├── doubao_demo.py         # API 客户端
    ├── cli.py                # 命令行接口
    └── doubao_skill_examples.py  # 使用示例
```

## 🚀 集成方式

### 方式 1: CLI 命令行

```bash
cd ~/.openclaw/workspace/skills/doubao-skill/scripts

# 设置 API Key
export ARK_API_KEY="your_api_key"

# 使用 CLI
python3 cli.py img "一只可爱的小猫"
python3 cli.py edit "https://..." "remove watermark"
python3 cli.py vid "一个人在跳舞" async
python3 cli.py status "task_xxxxx"
```

### 方式 2: Python 导入

```python
import sys
import os

# 添加路径
sys.path.insert(0, '/path/to/doubao-skill/scripts')

from doubao_skill import handler

async def main():
    # 设置 API Key
    os.environ["ARK_API_KEY"] = "your_api_key"

    # 使用 Skill
    result = await handler({
        "action": "img",
        "prompt": "一只可爱的小猫"
    })
    
    print(result)
```

### 方式 3: OpenClaw 注册

```python
# 在 OpenClaw 中注册
from scripts.doubao_skill import skill

openclaw.register_skill(skill)

# 使用
response = await openclaw.execute_skill("doubao", {
    "action": "img",
    "prompt": "..."
})
```

## 📚 API 参考

### Action: img (文本生图)

```python
await handler({
    "action": "img",
    "prompt": "生成提示词"
})
```

**返回:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "prompt": "生成提示词"
}
```

---

### Action: edit (图片编辑)

```python
await handler({
    "action": "edit",
    "image_url": "https://...",
    "prompt": "remove watermark, keep main content"  # 可选
})
```

**返回:**
```json
{
  "status": "success",
  "image_url": "https://...",
  "prompt": "remove watermark, keep main content"
}
```

**功能:**
- 智能去除图片水印
- 保持主要内容不被裁剪
- 支持自定义编辑提示词

---

### Action: vid (文本生视频)

```python
await handler({
    "action": "vid",
    "prompt": "生成提示词",
    "sync_mode": "async"  # 或 "sync"
})
```

**返回 (async):**
```json
{
  "status": "success",
  "task_id": "task_xxxxx",
  "prompt": "生成提示词"
}
```

**返回 (sync):**
```json
{
  "status": "success",
  "result_url": "https://...",
  "prompt": "生成提示词"
}
```

---

### Action: status (查询任务状态)

```python
await handler({
    "action": "status",
    "task_id": "task_xxxxx"
})
```

**返回:**
```json
{
  "status": "running",  # 或 "succeeded", "failed"
  "progress": 50,
  "task_id": "task_xxxxx"
}
```

---

## ⚙️ 配置

### 环境变量

```bash
# 必需
export ARK_API_KEY="your_api_key"

# 可选
export LOG_LEVEL="DEBUG"
export REQUEST_TIMEOUT="300"
```

### 技能清单 (doubao-skill.json)

```json
{
  "name": "doubao",
  "version": "1.1.0",
  "capabilities": [
    "text-to-image",
    "image-editing",
    "text-to-video",
    "task-status-check"
  ]
}
```

## 💡 高级用法

### 批量处理

```python
import asyncio

prompts = ["猫", "狗", "鸟"]

async def batch_generate():
    tasks = [
        handler({"action": "img", "prompt": p})
        for p in prompts
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### 错误处理

```python
try:
    result = await handler({"action": "img", "prompt": "test"})
    
    if result["status"] == "success":
        print(f"成功: {result['image_url']}")
    else:
        print(f"错误: {result['error']}")
        
except Exception as e:
    print(f"异常: {e}")
```

## 🧪 测试

```bash
cd scripts

# 运行示例
python3 doubao_skill_examples.py

# CLI 测试
python3 cli.py help
```

## 📊 性能指标

| 操作 | 预期耗时 | 说明 |
|------|---------|------|
| 文生图 | 10-30 秒 | 取决于图片大小和服务器负载 |
| 图片编辑 | 10-30 秒 | 取决于编辑复杂度 |
| 文生视频（启动） | 1-5 秒 | 异步模式返回任务ID |
| 文生视频（完成） | 1-3 分钟 | 同步模式等待完成 |
| 状态查询 | < 1 秒 | 实时查询任务状态 |

---

**版本**: 1.1.0  
**维护者**: Doubao Skill Team
