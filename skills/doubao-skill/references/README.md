# Doubao Skill - 快速开始指南

## 📋 目录结构

```
doubao-skill/
├── SKILL.md                    # 技能主文档
├── README.md                   # 技能说明（本文件）
├── doubao-skill.json           # 技能配置清单
├── requirements.txt             # Python 依赖
├── references/                 # 参考文档
│   ├── README.md              # 快速开始指南（本文件）
│   ├── SKILL.md              # 详细技能文档
│   └── INTEGRATION_GUIDE.md  # 集成指南
└── scripts/                   # 执行脚本
    ├── cli.py                # CLI 命令行工具
    ├── doubao_demo.py         # API 客户端
    ├── doubao_skill.py        # 核心 Skill 实现
    └── doubao_skill_examples.py  # 使用示例
```

## 🚀 5分钟快速开始

### 步骤 1: 设置环境

```bash
# 设置 API Key
export ARK_API_KEY="your_api_key_here"

# 验证
echo $ARK_API_KEY
```

### 步骤 2: 安装依赖

```bash
cd ~/.openclaw/workspace/skills/doubao-skill
pip install -r requirements.txt
```

### 步骤 3: CLI 快速测试

```bash
# 进入 scripts 目录
cd scripts

# 生成图片
python3 cli.py img "一只可爱的小猫"

# 编辑图片（去除水印）
python3 cli.py edit "https://..." "remove watermark, keep main content"

# 生成视频
python3 cli.py vid "一个人在跳舞" async
```

### 步骤 4: Python 代码调用

```python
import asyncio
import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, '/path/to/doubao-skill/scripts')

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

### 步骤 5: 查看示例

```bash
cd scripts
python3 doubao_skill_examples.py
```

## 📖 CLI 命令参考

### 文生图

```bash
python3 cli.py img "提示词"
```

### 图片编辑（去除水印）

```bash
# 默认提示词
python3 cli.py edit "https://example.com/image.png"

# 自定义提示词
python3 cli.py edit "https://example.com/image.png" "remove logo, preserve subject"
```

### 文生视频

```bash
# 异步模式（返回任务 ID）
python3 cli.py vid "一个人在跳舞" async

# 同步模式（等待完成）
python3 cli.py vid "一个人在跳舞" sync
```

### 查询任务状态

```bash
python3 cli.py status "task_xxxxx"
```

## 🔧 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `ARK_API_KEY` | ✅ | Volcengine ARK API 密钥 |
| `LOG_LEVEL` | ❌ | 日志级别（DEBUG, INFO 等） |
| `REQUEST_TIMEOUT` | ❌ | 请求超时时间（秒） |

## 📊 快速参考

| 功能 | 命令 | 耗时 |
|------|------|------|
| 文生图 | `img` | 10-30 秒 |
| 图片编辑 | `edit` | 10-30 秒 |
| 文生视频（启动） | `vid` async | 1-5 秒 |
| 文生视频（完成） | `vid` sync | 1-3 分钟 |
| 状态查询 | `status` | < 1 秒 |

## 🆘 帮助

```bash
# 查看帮助信息
python3 cli.py help

# 查看详细文档
cat ../references/SKILL.md
cat ../references/INTEGRATION_GUIDE.md
```

---

**版本**: 1.1.0  
**最后更新**: 2026-03-02  
**维护者**: Doubao Skill Team
