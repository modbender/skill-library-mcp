# Pyzotero CLI v2.0.0 更新说明

## 重大变更

本次更新将 pyzotero-cli 从纯 CLI 工具重写为 Python 脚本调用方式，提供更灵活的集成能力。

## 新特性

### 1. Python 脚本调用方式

**v1.x (旧版):**
```bash
pyzotero search -q "machine learning"
```

**v2.x (新版):**
```bash
python3 scripts/pyzotero.py search -q "machine learning"
```

### 2. 双模式支持

新增 `ZOTERO_LOCAL` 环境变量，支持在本地 API 和在线 API 之间切换:

#### 本地模式 (默认)
```bash
export ZOTERO_LOCAL="true"
python3 scripts/pyzotero.py search -q "topic"
```
- 直接连接本地运行的 Zotero 7+
- 无需 API 密钥
- 快速、离线可用

#### 在线模式
```bash
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"
python3 scripts/pyzotero.py search -q "topic"
```
- 通过 Zotero Web API 访问
- 支持远程访问
- 需要 API 密钥

### 3. 完整功能同步

所有原版 pyzotero-cli 的功能都已保留:

- ✅ 基本搜索
- ✅ 全文搜索 (包括 PDF)
- ✅ 按项目类型过滤
- ✅ 按集合过滤
- ✅ JSON 输出
- ✅ 列出集合
- ✅ 列出项目类型
- ✅ 获取项目详情

## 迁移指南

### 从 v1.x 升级到 v2.x

1. **更新技能**
   ```bash
   cd /root/.openclaw/workspace/skills/pyzotero-cli
   # 技能已自动更新
   ```

2. **修改命令调用方式**
   
   旧版:
   ```bash
   pyzotero search -q "topic"
   ```
   
   新版:
   ```bash
   python3 scripts/pyzotero.py search -q "topic"
   ```

3. **设置环境变量 (可选)**
   ```bash
   # 添加到 ~/.bashrc 或 ~/.zshrc
   export ZOTERO_LOCAL="true"
   ```

### 创建快捷方式 (可选)

如果您希望继续使用简短的命令，可以创建别名或包装脚本:

**方法一：Shell 别名**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias pyzotero='python3 /root/.openclaw/workspace/skills/pyzotero-cli/scripts/pyzotero.py'
```

**方法二：包装脚本**
```bash
#!/bin/bash
python3 /root/.openclaw/workspace/skills/pyzotero-cli/scripts/pyzotero.py "$@"
```

保存为 `/usr/local/bin/pyzotero` 并添加执行权限:
```bash
chmod +x /usr/local/bin/pyzotero
```

## 文件结构变更

### v1.x
```
pyzotero-cli/
├── SKILL.md
├── README.md
├── QUICKSTART.md
├── INSTALL.md
└── EXAMPLES.md
```

### v2.x
```
pyzotero-cli/
├── SKILL.md               (已更新)
├── README.md
├── QUICKSTART.md          (已更新)
├── INSTALL.md
├── EXAMPLES.md
├── _meta.json             (版本更新为 2.0.0)
└── scripts/               (新增)
    ├── pyzotero.py        (新增 - 主脚本)
    └── examples.py        (新增 - 示例脚本)
```

## 环境变量参考

| 变量名 | 必需性 | 默认值 | 说明 |
|--------|--------|--------|------|
| `ZOTERO_LOCAL` | 否 | `"true"` | `"true"`=本地模式，`"false"`=在线模式 |
| `ZOTERO_USER_ID` | 在线模式必需 | - | Zotero 用户 ID |
| `ZOTERO_API_KEY` | 在线模式必需 | - | Zotero API 密钥 |

## 兼容性

- **Python 版本:** Python 3.6+
- **pyzotero 库版本:** 最新版本
- **Zotero 版本:** 
  - 本地模式：Zotero 7+
  - 在线模式：任意版本 (通过 Web API)

## 已知问题

无已知问题。

## 后续计划

- [ ] 添加批量操作支持
- [ ] 支持写入操作 (创建、修改、删除项目)
- [ ] 添加同步功能
- [ ] 支持附件管理
- [ ] 添加注释和高亮管理

## 反馈与支持

如有问题或建议，请在 OpenClaw 社区反馈。

---

**发布日期:** 2026-02-23  
**版本:** 2.0.0  
**破坏性变更:** 是 (命令调用方式变更)
