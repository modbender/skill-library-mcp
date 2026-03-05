# 飞书文档(Docx)技能

用于操作飞书文档的完整技能，支持文档的CRUD操作和内容管理。

## 版本历史

### v1.0.1 (2026-02-09)
- **修复**: 修复了创建文档时内容无法写入的问题
- **优化**: 改进了文档内容追加功能
- **新增**: 添加了 `appendToDocument` API方法
- **改进**: 优化了CLI工具的 `update` 命令逻辑

### v1.0.0 (初始版本)
- 初始发布，支持基本的文档CRUD操作

## 功能特性

- ✅ 文档管理（创建、获取、更新、删除）
- ✅ 文档内容操作（读取、写入、追加）
- ✅ 文档权限管理（分享、权限设置）
- ✅ 文档搜索和列表
- ✅ 文档导出为Markdown

## 安装

### 1. 克隆技能到本地
```bash
git clone <repository-url> skills/feishu-docs
cd skills/feishu-docs
```

### 2. 安装依赖
```bash
npm install
```

### 3. 设置环境变量
```bash
# 飞书应用ID
export FEISHU_APP_ID=cli_xxxxxx

# 飞书应用密钥
export FEISHU_APP_SECRET=your_app_secret
```

或者创建 `.env` 文件：
```env
FEISHU_APP_ID=cli_xxxxxx
FEISHU_APP_SECRET=your_app_secret
```

## 使用方法

### 命令行工具

```bash
# 显示帮助
node bin/cli.js --help

# 创建新文档
node bin/cli.js create \
  --folder-token fldxxxxxx \
  --title "项目计划" \
  --content "# 项目概述\n\n## 目标\n- 完成开发\n- 测试通过"

# 获取文档信息
node bin/cli.js get --document-id dcnxxxxxx

# 更新文档内容
node bin/cli.js update \
  --document-id dcnxxxxxx \
  --content "# 更新内容"

# 删除文档
node bin/cli.js delete --document-id dcnxxxxxx

# 搜索文档
node bin/cli.js search --query "项目"

# 列出文件夹中的文档
node bin/cli.js list --folder-token fldxxxxxx

# 分享文档
node bin/cli.js share \
  --document-id dcnxxxxxx \
  --user-id ou_xxxxxx \
  --perm edit

# 导出文档为Markdown
node bin/cli.js export \
  --document-id dcnxxxxxx \
  --output project-plan.md
```

### 在Clawdbot中使用

1. **确保技能已安装**：技能应该位于 `skills/feishu-docs` 目录
2. **设置环境变量**：在Clawdbot配置中设置飞书应用凭证
3. **在对话中调用**：Clawdbot可以调用此技能来操作飞书文档

#### 示例对话

**用户**: "帮我在飞书创建一个项目文档"
**Clawdbot**: 
```bash
# 使用技能创建文档
node skills/feishu-docs/bin/cli.js create \
  --folder-token fldxxxxxx \
  --title "项目文档" \
  --content "# 项目概述\n\n## 目标\n- 完成系统开发\n- 通过测试\n- 上线运行"
```

**用户**: "获取文档内容"
**Clawdbot**: 
```bash
# 使用技能获取文档
node skills/feishu-docs/bin/cli.js get \
  --document-id dcnxxxxxx \
  --include-content \
  --format markdown
```

## API参考

### FeishuDocsAPI类

```javascript
const FeishuDocsAPI = require('./src/api.js');

// 初始化
const api = new FeishuDocsAPI(appId, appSecret);

// 创建文档
const result = await api.createDocument(folderToken, title, content);

// 获取文档
const document = await api.getDocument(documentId);

// 获取文档块
const blocks = await api.getDocumentBlocks(documentId);

// 更新文档块
await api.updateDocumentBlock(documentId, blockId, updateRequest);

// 删除文档
await api.deleteDocument(documentId);

// 搜索文档
const results = await api.searchDocuments(query, folderToken);

// 分享文档
await api.addPermissionMember(documentId, userId, 'user', 'edit');

// 获取权限成员
const members = await api.getPermissionMembers(documentId);
```

### 文档块结构

飞书文档使用块(block)结构组织内容，支持以下类型：
- `page` - 页面块
- `text` - 文本块
- `heading` - 标题块
- `bullet` - 无序列表
- `ordered` - 有序列表
- `code` - 代码块
- `quote` - 引用块
- `callout` - 标注块
- `divider` - 分割线

## 配置飞书应用

### 1. 创建飞书应用
1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 记录应用ID和密钥

### 2. 配置权限
应用需要以下权限：
- `drive:drive:readonly` - 读取云文档
- `drive:drive:write` - 写入云文档
- `drive:file:readonly` - 读取文件
- `drive:file:write` - 写入文件

### 3. 发布应用
1. 创建版本
2. 申请发布
3. 等待审核通过

## 注意事项

1. **权限要求**：确保应用已获得必要的API权限
2. **速率限制**：飞书API有速率限制，建议添加适当的延迟
3. **文档大小**：单次更新内容不宜过大
4. **内容格式**：支持Markdown格式转换为飞书文档格式
5. **错误处理**：所有API调用都有错误处理，会提供有意义的错误信息

## 开发指南

### 项目结构
```
feishu-docs/
├── bin/
│   └── cli.js          # 命令行接口
├── src/
│   └── api.js          # API客户端
├── package.json        # 项目配置
├── README.md           # 说明文档
└── SKILL.md           # Clawdbot技能定义
```

### 添加新功能
1. 在 `src/api.js` 的 `FeishuDocsAPI` 类中添加新方法
2. 在 `bin/cli.js` 中添加对应的命令
3. 更新文档

### 测试
```bash
# 测试创建文档
node bin/cli.js create --help

# 测试获取文档
node bin/cli.js get --help
```

## 故障排除

### 常见问题

1. **认证失败**
   - 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
   - 确保应用已发布并获得权限

2. **权限不足**
   - 检查应用是否已获得必要的API权限
   - 确保应用已发布

3. **网络错误**
   - 检查网络连接
   - 确认飞书API服务状态

4. **文档操作失败**
   - 检查文档ID是否正确
   - 确认有操作该文档的权限

### 获取帮助
- 查看飞书开放平台文档：https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/overview
- 检查技能日志
- 联系开发者

## 许可证

MIT License