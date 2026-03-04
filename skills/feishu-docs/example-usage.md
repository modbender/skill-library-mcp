# 飞书文档技能使用示例

## 问题背景
在之前的版本中，feishu-docs技能包缺少飞书官方文档中提到的转换接口（`POST /docx/v1/documents/blocks/convert`），导致Markdown内容无法正确插入到文档中。

## 解决方案
版本 1.1.0 添加了完整的转换接口支持，现在可以正确地将Markdown/HTML内容插入到飞书文档中。

## 使用示例

### 1. 命令行使用

#### 创建文档并正确插入Markdown内容（推荐）
```bash
# 设置环境变量
export FEISHU_APP_ID=cli_xxxxxx
export FEISHU_APP_SECRET=your_app_secret

# 创建文档并插入内容
node bin/cli.js create-with-content \
  --folder-token fldxxxxxx \
  --title "项目文档" \
  --content "# 项目概述\n\n## 目标\n- 完成开发\n- 测试通过\n- 上线运行\n\n## 时间安排\n- 第一周：需求分析\n- 第二周：开发实现"
```

#### 从文件创建文档
```bash
node bin/cli.js create-with-content \
  --folder-token fldxxxxxx \
  --title "技术文档" \
  --content-file README.md
```

#### 转换内容为文档块
```bash
# 转换Markdown内容
node bin/cli.js convert \
  --content-type markdown \
  --content "# 标题\n\n这是**加粗**文本"

# 转换HTML内容
node bin/cli.js convert \
  --content-type html \
  --content "<h1>标题</h1><p>这是<strong>加粗</strong>文本</p>"
```

### 2. 在代码中使用

```javascript
const FeishuDocsAPI = require('./src/api.js');

async function createDocumentWithMarkdown() {
  const api = new FeishuDocsAPI('cli_xxxxxx', 'your_app_secret');
  
  const markdownContent = `# API文档

## 接口列表

### 用户管理
1. GET /api/users - 获取用户列表
2. POST /api/users - 创建用户
3. PUT /api/users/{id} - 更新用户

### 订单管理
- GET /api/orders
- POST /api/orders
- DELETE /api/orders/{id}

## 代码示例

\`\`\`javascript
// 获取用户列表
async function getUsers() {
  const response = await fetch('/api/users');
  return response.json();
}
\`\`\`

## 注意事项
> 所有接口都需要认证
> 使用HTTPS协议`;

  try {
    // 方法1：使用新的createDocumentWithContent方法（推荐）
    const result = await api.createDocumentWithContent(
      'fldxxxxxx', // 文件夹token
      'API文档',   // 文档标题
      markdownContent, // Markdown内容
      'markdown'  // 内容类型
    );
    
    console.log('文档创建成功:', result.document.document_id);
    
    // 方法2：手动转换并插入（更灵活的控制）
    const convertResult = await api.convertContent('markdown', markdownContent);
    
    // 将转换后的块插入到现有文档
    const insertResult = await api.createDocumentBlocks(
      'dcnxxxxxx', // 文档ID
      'dcnxxxxxx', // 父块ID（通常是文档ID）
      convertResult.blocks, // 转换后的块
      0 // 插入位置
    );
    
    console.log('内容插入成功');
    
  } catch (error) {
    console.error('操作失败:', error.message);
  }
}

createDocumentWithMarkdown();
```

### 3. 在Clawdbot中使用

```bash
# 在Clawdbot对话中创建文档
用户: "帮我在飞书创建一个API文档"

Clawdbot: 
# 使用更新后的技能包
node skills/feishu-docs/bin/cli.js create-with-content \
  --folder-token fldxxxxxx \
  --title "API文档" \
  --content "# API接口说明\n\n## 用户接口\n- GET /users\n- POST /users\n\n## 订单接口\n- GET /orders\n- POST /orders"
```

## 重要注意事项

### 1. 权限配置
在飞书开放平台中，确保应用已添加以下权限：
- `drive:drive:readonly` - 读取云文档
- `drive:drive:write` - 写入云文档
- `文本内容转换为云文档块` - 内容转换权限（新增）

### 2. 内容大小限制
- 单次转换内容：不超过10MB（10485760字符）
- 单次插入块数：不超过1000个块
- 大内容需要分批处理

### 3. 特殊内容处理
- **表格**：自动处理`merge_info`字段
- **图片**：需要额外上传图片素材
- **代码块**：支持语法高亮

### 4. 错误处理
```javascript
try {
  await api.createDocumentWithContent(folderToken, title, content);
} catch (error) {
  if (error.message.includes('content size exceed limit')) {
    console.error('内容太大，请减少内容后重试');
  } else if (error.message.includes('permission denied')) {
    console.error('权限不足，请检查应用权限配置');
  } else {
    console.error('操作失败:', error.message);
  }
}
```

## 迁移指南

### 从旧版本迁移
如果你之前使用`create`命令：
```bash
# 旧方式（不推荐）
node bin/cli.js create --folder-token fldxxxxxx --title "文档" --content "# 标题"

# 新方式（推荐）
node bin/cli.js create-with-content --folder-token fldxxxxxx --title "文档" --content "# 标题"
```

### 在代码中迁移
```javascript
// 旧方式
const result = await api.createDocument(folderToken, title, content);

// 新方式
const result = await api.createDocumentWithContent(folderToken, title, content);
```

## 测试验证
运行测试脚本验证转换接口是否工作正常：
```bash
npm run test:convert
```

## 获取帮助
```bash
# 查看所有命令
node bin/cli.js --help

# 查看特定命令帮助
node bin/cli.js create-with-content --help
node bin/cli.js convert --help
```

## 常见问题

### Q: 为什么我的Markdown内容没有正确显示？
A: 确保使用`create-with-content`命令而不是`create`命令。`create`命令将内容放在title字段中，不会正确解析Markdown。

### Q: 转换接口返回错误怎么办？
A: 检查应用权限是否包含`文本内容转换为云文档块`，并确保内容大小不超过限制。

### Q: 如何插入大量内容？
A: 大内容会自动分批插入，每批最多1000个块。如果仍有问题，可以手动分批处理。

### Q: 支持哪些Markdown语法？
A: 支持标题、列表、代码块、引用、表格、加粗、斜体、删除线、行内代码、链接等基本语法。