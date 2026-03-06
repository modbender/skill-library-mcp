---
name: xhs-auto
description: 小红书自动化发布流程，串联主题输入、图像生成、文案草拟与 debug 发布校验。
metadata: {"openclaw": {"emoji": "🤖", "requires": {"bins": ["bash", "curl", "jq", "base64", "xhs-kit"]}}}
---

# 小红书自动化内容发布

用户输入主题和想法，自动化生成小红书文案和配图，调用 `xhs-kit` 发布（测试环境用 `xhs-kit debug-publish`）。

0. 输出内容（文案、配图等）在 `${workspace}/xhs-auto/{timestamp}` 目录下。
1. 用户输入主题和想法。
2. 判断是否有图片，如果有图片则跳过图片生成阶段；如果没有图片，构造生图 Prompt，并调用 `scripts/xhs-image.sh` 生成图片。
3. 调用 `xhs-kit debug-publish` 校验内容合规，输出详细报告。

## 目录结构
```
.claude/skills/xhs-auto/
├── SKILL.md                    # 本文档
├── scripts/
│   ├── xhs-image.py            # 图像生成脚本（Python，推荐）
│   └── xhs-image.sh            # 图像生成脚本（Bash，备选）
└── references/
    ├── text-to-image.md        # 图像生成详细指南
    └── publish.md              # 小红书发布指南
```

## 环境准备

```bash
# 安装 xhs-kit
pip install xhs-kit

# 安装 Playwright 浏览器（用于正式发布时登录）
playwright install chromium

# 安装图片生成依赖（Python 版本）
pip install requests
```

## 完整流程

### 步骤1. 确定文案

“帮我写篇小红书笔记”、“帮我发一篇小红书”。了解用户的主题和想法。生成标题和正文。标题小于20字，正文小于950字。如果用户有图片，则跳过步骤2；如果没有图片，进入步骤2。生成内容到 `${workspace}/xhs-auto/{datetime}/{keyword}.md`：
- 标题
- 正文
- tags
- 图片路径，如果用户已提供图片
- 图片生成提示词，如果用户没有提供图片，每一张图一个 Prompt。

### 步骤2. 生成图片

询问用户希望文生图还是图生图，并根据步骤1的主题和文案，生成生图 Prompt 和图片数量。

参考 `references/text-to-image.md`，调用 `scripts/xhs-image.py`（推荐）或 `scripts/xhs-image.sh` 进行图片生成。

**Python 版本示例：**
```bash
python scripts/xhs-image.py \
  --mode generate \
  --prompt "小红书风格的下午茶摆拍" \
  --ratio 1:1 \
  --output workspace/xhs-auto/20260301-143022/image.png
```

### 步骤3. 发布内容

参考 `references/publish.md` ，调用 `xhs-kit` 测试接口 `debug-publish` 发布内容。


## 常见问题

### 图片生成相关
- **推荐使用 Python 版本（xhs-image.py）**：跨平台兼容性更好，特别是 Windows 用户
- **ModuleNotFoundError: No module named 'requests'**：执行 `pip install requests`
- **Bash 版本在 Windows 上无法运行**：建议使用 Python 版本，或安装 WSL/Git Bash
- **国内网络访问模型失败**：配置国内可用的 API 中转服务，设置 `GOOGLE_API_BASE` 环境变量

### 发布相关
- **debug-publish 报错图片不存在**：确保图片路径正确且文件存在
- **未登录错误**：正式发布前需要先执行 `xhs-kit login-qrcode --terminal`

详细说明请参考 `references/text-to-image.md` 和 `references/publish.md`。