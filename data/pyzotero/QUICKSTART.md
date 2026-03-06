# Pyzotero CLI 快速入门

5 分钟快速开始使用 Python 脚本管理您的 Zotero 库。

## 1. 安装 pyzotero 库 (2 分钟)

### 推荐方式 (pipx)
```bash
pipx install pyzotero
```

### 备选方式 (pip)
```bash
pip install --user pyzotero
export PATH="$HOME/.local/bin:$PATH"
```

## 2. 配置访问模式 (1 分钟)

### 模式一：本地模式 (推荐)

**适用场景:** Zotero 7+ 已安装在本地，需要快速访问

**配置步骤:**
1. 打开 Zotero 7 (或更新版本)
2. 进入 **编辑 > 首选项 > 高级**
3. 勾选 **"允许此计算机上的其他应用程序与 Zotero 通信"**
4. 重启 Zotero

**验证配置:**
```bash
export ZOTERO_LOCAL="true"
python3 scripts/zotero_tool.py listcollections
```

### 模式二：在线模式

**适用场景:** 需要远程访问 Zotero 库，或在无 Zotero 安装的服务器上运行

**配置步骤:**
1. 访问 https://www.zotero.org/settings/keys
2. 点击 "Create new private key"
3. 授予读取权限
4. 复制密钥并设置环境变量:

```bash
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"
```

**验证配置:**
```bash
python3 scripts/zotero_tool.py listcollections
```

## 3. 基本命令 (2 分钟)

### 搜索文献
```bash
# 基本搜索
python3 scripts/zotero_tool.py search -q "machine learning"

# 全文搜索 (包括 PDF 内容)
python3 scripts/zotero_tool.py search -q "neural networks" --fulltext

# 按类型过滤
python3 scripts/zotero_tool.py search -q "python" --itemtype journalArticle

# 限制结果数量
python3 scripts/zotero_tool.py search -q "deep learning" -l 10
```

### 浏览集合
```bash
# 列出所有集合
python3 scripts/zotero_tool.py listcollections
```

### 查看项目类型
```bash
# 列出所有项目类型
python3 scripts/zotero_tool.py itemtypes
```

### 获取项目详情
```bash
# 获取单个项目 (需要项目密钥)
python3 scripts/zotero_tool.py item ABC123XYZ
```

## 4. 输出格式

### 人类可读格式 (默认)
```bash
python3 scripts/zotero_tool.py search -q "python"
```

输出示例:
```
找到 3 个项目:

1. [journalArticle] Python Machine Learning
   作者：Sebastian Raschka
   年份：2015
   标签：machine-learning, python
   链接：https://www.zotero.org/user/items/ABC123
```

### JSON 格式
```bash
python3 scripts/zotero_tool.py search -q "python" --json
```

使用 jq 处理:
```bash
# 提取标题
python3 scripts/zotero_tool.py search -q "python" --json | jq '.[].data.title'

# 统计数量
python3 scripts/zotero_tool.py search -q "python" --json | jq 'length'

# 保存到文件
python3 scripts/zotero_tool.py search -q "python" --json > results.json
```

## 5. 常用工作流

### 每日文献回顾
```bash
# 搜索最近添加的机器学习文献
python3 scripts/zotero_tool.py search -q "machine learning" -l 20

# 导出为 JSON 进行进一步处理
python3 scripts/zotero_tool.py search -q "machine learning" --json > daily_review.json
```

### 按主题整理
```bash
# 搜索特定主题的期刊文章
python3 scripts/zotero_tool.py search -q "deep learning" --itemtype journalArticle

# 搜索特定集合中的内容
python3 scripts/zotero_tool.py search --collection ABC123 -q "test"
```

### 快速获取引用信息
```bash
# 获取特定项目的详细信息
python3 scripts/zotero_tool.py item ITEM_KEY

# 获取 JSON 格式用于引用管理
python3 scripts/zotero_tool.py item ITEM_KEY --json
```

## 6. 故障排除

### 本地模式连接失败
```
问题：无法连接到本地 Zotero

解决方案:
1. 确保 Zotero 正在运行
2. 检查是否启用本地 API: 
   设置 > 高级 > "允许此计算机上的其他应用程序与 Zotero 通信"
3. 重启 Zotero
```

### 在线模式认证失败
```
问题：API 认证错误

解决方案:
1. 检查 ZOTERO_USER_ID 是否正确
2. 检查 ZOTERO_API_KEY 是否有效
3. 确认 ZOTERO_LOCAL="false"
```

### 模块未找到
```
问题：ModuleNotFoundError: No module named 'pyzotero'

解决方案:
pipx install pyzotero
# 或
pip install --user pyzotero
```

## 7. 下一步

- 📖 阅读 [INSTALL.md](INSTALL.md) 了解详细安装指南
- 💡 查看 [EXAMPLES.md](EXAMPLES.md) 获取更多使用示例
- 📚 参考 [README.md](README.md) 了解完整功能
- 🔧 查看 [SKILL.md](SKILL.md) 获取完整命令参考

## 命令速查表

```bash
# 环境设置
export ZOTERO_LOCAL="true"                    # 本地模式
export ZOTERO_LOCAL="false"                   # 在线模式
export ZOTERO_USER_ID="your_id"              # 在线模式用户 ID
export ZOTERO_API_KEY="your_key"             # 在线模式 API 密钥

# 搜索
python3 scripts/zotero_tool.py search -q "关键词"
python3 scripts/zotero_tool.py search -q "关键词" --fulltext
python3 scripts/zotero_tool.py search -q "关键词" --itemtype journalArticle
python3 scripts/zotero_tool.py search -q "关键词" --json

# 浏览
python3 scripts/zotero_tool.py listcollections
python3 scripts/zotero_tool.py itemtypes

# 获取详情
python3 scripts/zotero_tool.py item ITEM_KEY
```

---

**提示:** 将常用命令添加到您的 `~/.bashrc` 或 `~/.zshrc` 中以便快速访问！
