# 飞书文档创建技能包 (Feishu Document Skills)

将 Markdown 文件转换为飞书文档的完整技能包。

## 功能

- ✅ Markdown 解析为飞书文档格式（支持 25 种块类型）
- ✅ 本地图片自动上传（`![alt](D:/path/to/image.png)`）
- ✅ 自动文档创建 + 权限管理（添加协作者 + 转移所有权）
- ✅ 智能 Token 模式选择
- ✅ 分批添加内容块
- ✅ Playwright 文档验证（自动保存登录状态）
- ✅ 完整的日志记录

## 包含的技能

| 技能 | 说明 |
|-----|------|
| `feishu-md-parser` | Markdown 解析器 |
| `feishu-doc-creator-with-permission` | 文档创建 + 权限管理 |
| `feishu-block-adder` | 块添加器 |
| `feishu-doc-verifier` | 文档验证器 |
| `feishu-logger` | 日志记录器 |
| `feishu-doc-orchestrator` | 主编排器 |

## 快速开始

### 1. 安装依赖

```bash
pip install playwright requests lark-oapi
playwright install chromium
```

### 2. 配置飞书应用

复制配置模板并填写凭证：

```bash
cp feishu-config.env.template .claude/feishu-config.env
```

编辑 `.claude/feishu-config.env`，填写你的飞书应用凭证：

```ini
FEISHU_APP_ID = "cli_xxxxxxxxxxxxx"
FEISHU_APP_SECRET = "xxxxxxxxxxxxxxxxxx"
FEISHU_API_DOMAIN = "https://open.feishu.cn"
FEISHU_AUTO_COLLABORATOR_ID = "ou_xxxxxxxxxxxxxxxx"
```

### 3. OAuth 授权

```bash
python skills/feishu-doc-creator-with-permission/scripts/auto_auth.py
```

使用飞书 APP 扫码登录即可。

### 4. 创建文档

```bash
python skills/feishu-doc-orchestrator/scripts/orchestrator.py input.md "文档标题"
```

## 工作流程

```
input.md
    ↓
[1. Markdown 解析] → blocks.json
    ↓
[2. 文档创建 + 权限管理] → doc_with_permission.json
    ↓
[3. 块添加] → add_result.json
    ↓
[4. 文档验证] → verify_result.json
    ↓
[5. 日志记录] → CREATED_DOCS.md
```

## 配置说明

| 配置项 | 必填 | 说明 |
|-------|-----|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用密钥 |
| `FEISHU_API_DOMAIN` | ❌ | API 地址，默认 `https://open.feishu.cn` |
| `FEISHU_AUTO_COLLABORATOR_ID` | 推荐 | 你的飞书用户 ID |

## 获取飞书应用凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建自建应用
3. 获取 App ID 和 App Secret
4. 申请权限：
   - `drive:drive` - 云文档
   - `docs:doc` - 查看文档
   - `docx:document` - 创建和编辑
   - `docs:permission.member:create` - 协作者管理

## 工具脚本

| 脚本 | 说明 |
|-----|------|
| `check_config.py` | 检查配置是否正确 |
| `auto_auth.py` | OAuth 自动授权 |
| `orchestrator.py` | 主编排脚本 |

## 检查配置

```bash
python skills/feishu-doc-orchestrator/scripts/check_config.py
```

## 系统要求

- Python >= 3.8
- playwright >= 1.40.0
- requests >= 2.31.0
- lark-oapi >= 1.2.0

## 许可证

MIT License
