# Doubao Skill

Doubao AI Generation - 文本生图、图片编辑和文本生视频技能

## 目录结构

```
doubao-skill/
├── SKILL.md                    # 技能主文档
├── README.md                   # 技能说明（本文件）
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

## 功能特性

- ✅ **文本生图** (Text-to-Image)
- ✅ **图片编辑** (Image Editing) - 去除水印
- ✅ **文本生视频** (Text-to-Video)
- ✅ **任务状态查询** (Task Status Check)

## 快速开始

### 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export ARK_API_KEY="your_api_key_here"
```

### 使用

```bash
# 进入 scripts 目录
cd scripts

# 生成图片
python3 cli.py img "一只可爱的小猫"

# 编辑图片（去除水印）
python3 cli.py edit "https://..." "remove watermark, keep main content"

# 生成视频
python3 cli.py vid "一个人在跳舞" async

# 检查任务状态
python3 cli.py status "task_xxxxx"
```

## 详细文档

查看 `references/` 目录获取更多详细信息：
- `references/README.md` - 快速开始指南
- `references/SKILL.md` - 详细技能文档
- `references/INTEGRATION_GUIDE.md` - 集成指南
- `CHANGELOG.md` - 更新日志

## 版本信息

- **版本**: 1.1.0
- **作者**: Doubao Skill Team
- **最后更新**: 2026-03-02
- **API**: Volcengine ARK (ByteDance/Doubao)

## 技术要求

- Python 3.7+
- ARK_API_KEY (从 https://console.volcengine.com/ark 获取)
- 依赖: requests, aiohttp, pydantic, pytimeparse
