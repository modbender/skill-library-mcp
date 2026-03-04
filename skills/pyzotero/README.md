# Pyzotero CLI Skill for OpenClaw

使用 Python 脚本调用 pyzotero 库，支持本地 Zotero API 和在线 Web API 两种模式。

## 📦 包含内容

### 核心文档
- **[SKILL.md](SKILL.md)** - 完整技能文档，包含功能、安装和命令参考
- **[INSTALL.md](INSTALL.md)** - 详细安装指南，支持 PEP 668/pipx
- **[QUICKSTART.md](QUICKSTART.md)** - 5 分钟快速入门
- **[EXAMPLES.md](EXAMPLES.md)** - 实用命令行示例和工作流
- **[CHANGELOG_v2.md](CHANGELOG_v2.md)** - v2.0.0 更新说明
- **[README.md](README.md)** - 本文件 - 项目概览

### Python 脚本
- **scripts/zotero_tool.py** - 主脚本，提供完整的 Zotero 库管理功能
- **scripts/examples.py** - 示例脚本，展示各种使用场景

## 🚀 快速开始

### 1. 安装 pyzotero 库

**使用 pipx (推荐):**
```bash
pipx install pyzotero
```

**使用 pip:**
```bash
pip install --user pyzotero
export PATH="$HOME/.local/bin:$PATH"
```

### 2. 配置访问模式

**本地模式 (默认，推荐):**
```bash
export ZOTERO_LOCAL="true"
# 确保 Zotero 7+ 正在运行，并在 设置 > 高级 中启用本地 API
```

**在线模式:**
```bash
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"
```

### 3. 基本使用

```bash
cd /root/.openclaw/workspace/skills/pyzotero-cli

# 列出所有集合
python3 scripts/zotero_tool.py listcollections

# 搜索文献
python3 scripts/zotero_tool.py search -q "machine learning"

# 全文搜索 (包括 PDF)
python3 scripts/zotero_tool.py search -q "neural networks" --fulltext

# 获取项目详情
python3 scripts/zotero_tool.py item ABC123XYZ
```

## 🎯 核心功能

### 搜索功能
- ✅ 基本关键词搜索
- ✅ 全文搜索 (包括 PDF 附件)
- ✅ 按项目类型过滤 (期刊文章、书籍、会议论文等)
- ✅ 按集合过滤
- ✅ 限制结果数量
- ✅ JSON 输出格式

### 浏览功能
- ✅ 列出所有集合
- ✅ 列出项目类型
- ✅ 获取单个项目详情

### 访问模式
- ✅ **本地模式**: 直接连接本地 Zotero 7+，快速、离线可用
- ✅ **在线模式**: 通过 Zotero Web API 远程访问

### 输出格式
- ✅ 人类可读格式 (默认)
- ✅ JSON 格式 (用于自动化处理)

## 🌟 v2.0.0 新特性

### 1. Python 脚本调用方式

从 CLI 工具改为 Python 脚本，更灵活且易于集成:

**v1.x (旧版):**
```bash
pyzotero search -q "topic"
```

**v2.x (新版):**
```bash
python3 scripts/zotero_tool.py search -q "topic"
```

### 2. 双模式支持

新增 `ZOTERO_LOCAL` 环境变量，支持本地和在线 API 切换:

```bash
# 本地模式 (默认)
export ZOTERO_LOCAL="true"

# 在线模式
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"
```

### 3. 完整功能同步

所有原版 pyzotero-cli 功能都已保留并改进。

## 📊 使用场景

### 场景 1: 每日文献回顾
```bash
python3 scripts/zotero_tool.py search -q "machine learning" -l 10
```

### 场景 2: 按主题整理文献
```bash
python3 scripts/zotero_tool.py search -q "deep learning" --itemtype journalArticle
```

### 场景 3: 导出文献数据
```bash
python3 scripts/zotero_tool.py search -q "python" --json > results.json
```

### 场景 4: 自动化工作流
```python
# 在 Python 脚本中调用
import subprocess
subprocess.run(['python3', 'scripts/zotero_tool.py', 'search', '-q', 'topic'])
```

## 🔧 环境变量

| 变量名 | 必需性 | 默认值 | 说明 |
|--------|--------|--------|------|
| `ZOTERO_LOCAL` | 否 | `"true"` | `"true"`=本地模式，`"false"`=在线模式 |
| `ZOTERO_USER_ID` | 在线模式必需 | - | Zotero 用户 ID |
| `ZOTERO_API_KEY` | 在线模式必需 | - | Zotero API 密钥 |

## 📚 文档结构

### 入门文档
- **[QUICKSTART.md](QUICKSTART.md)** - 5 分钟快速开始
- **[INSTALL.md](INSTALL.md)** - 详细安装和配置指南

### 参考文档
- **[SKILL.md](SKILL.md)** - 完整技能和命令参考
- **[EXAMPLES.md](EXAMPLES.md)** - 实用示例和工作流

### 其他
- **[CHANGELOG_v2.md](CHANGELOG_v2.md)** - v2.0.0 更新说明
- **[README.md](README.md)** - 项目概览 (本文件)

## 🛠️ 故障排除

### 本地模式连接失败
```
解决方案:
1. 确保 Zotero 正在运行
2. 启用本地 API: 设置 > 高级 > "允许此计算机上的其他应用程序与 Zotero 通信"
3. 重启 Zotero
```

### 模块未找到
```bash
pipx install pyzotero
# 或
pip install --user pyzotero
```

### 在线模式认证失败
```bash
# 检查环境变量
echo $ZOTERO_LOCAL
echo $ZOTERO_USER_ID
echo $ZOTERO_API_KEY

# 确认设置为在线模式
export ZOTERO_LOCAL="false"
```

## 📖 完整文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 5 分钟快速入门 |
| [INSTALL.md](INSTALL.md) | 详细安装指南 |
| [SKILL.md](SKILL.md) | 完整技能和命令参考 |
| [EXAMPLES.md](EXAMPLES.md) | 实用示例和工作流 |
| [CHANGELOG_v2.md](CHANGELOG_v2.md) | v2.0.0 更新说明 |

## 🎓 学习路径

1. **快速开始** → 阅读 [QUICKSTART.md](QUICKSTART.md)
2. **安装配置** → 参考 [INSTALL.md](INSTALL.md)
3. **基本使用** → 查看 [SKILL.md](SKILL.md) 的核心命令
4. **高级用法** → 学习 [EXAMPLES.md](EXAMPLES.md) 的工作流
5. **深入了解** → 阅读 [CHANGELOG_v2.md](CHANGELOG_v2.md) 了解更新详情

## 💡 提示

- 将常用命令添加到 `~/.bashrc` 或 `~/.zshrc` 中
- 使用 JSON 输出配合 `jq` 进行数据处理
- 本地模式更快且无需 API 密钥 (推荐)
- 在线模式适合远程访问和服务器部署

---

**版本:** 2.0.0  
**更新日期:** 2026-02-23  
**许可:** 同 pyzotero 库许可

**上游项目:** https://github.com/urschrei/pyzotero
