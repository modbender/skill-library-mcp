# 安全最佳实践

## 核心原则

**永远不要将用户输入直接传递给 shell 命令或文件系统操作！**

这是最常见也是最危险的安全漏洞之一。

## 常见安全漏洞

### 1. 命令注入漏洞

#### ❌ 危险示例

```javascript
// 用户输入："; rm -rf / #"
const userInput = callback.data.action.value.file;
await exec({ command: `rm ${userInput}` });
// 实际执行：rm ; rm -rf / #
// 结果：删除整个系统！
```

### ✅ 安全做法

```javascript
// 使用 Node.js 内置 API
const fs = require('fs').promises;
const path = require('path');

const userInput = callback.data.action.value.file;

// 1. 验证和规范化路径
const safePath = path.resolve(userInput);

// 2. 检查路径是否在允许的范围内
const workspaceRoot = process.cwd();
if (!safePath.startsWith(workspaceRoot)) {
  throw new Error('路径超出工作区范围');
}

// 3. 使用安全的 API
await fs.unlink(safePath);
```

### 2. 任意文件读取漏洞

#### ❌ 危险示例

```javascript
// 用户输入："/etc/passwd" 或 "~/.ssh/id_rsa"
const templatePath = args['--template'];
const content = fs.readFileSync(templatePath, 'utf8');
// 攻击者可以读取系统中的任意文件！
```

#### ✅ 安全做法

```javascript
const path = require('path');
const fs = require('fs');

const templatePath = args['--template'];

// 1. 规范化路径
const resolvedPath = path.resolve(templatePath);

// 2. 定义允许的目录白名单
const allowedDirs = [
  path.join(__dirname, '..', 'examples'),
  path.join(__dirname, '..', 'templates')
];

// 3. 检查路径是否在白名单内
const isAllowed = allowedDirs.some(dir => resolvedPath.startsWith(dir));

if (!isAllowed) {
  throw new Error('路径不在允许的目录范围内');
}

// 4. 检查文件扩展名
const ext = path.extname(resolvedPath).toLowerCase();
const allowedExtensions = ['.json', '.txt', '.md'];
if (!allowedExtensions.includes(ext)) {
  throw new Error('不支持的文件类型');
}

// 5. 安全读取
const content = fs.readFileSync(resolvedPath, 'utf8');
```

## 输入验证

### 文件路径验证

```javascript
function validateFilePath(userPath) {
  const path = require('path');
  
  // 1. 规范化路径（解析 ../ 等）
  const normalized = path.resolve(userPath);
  
  // 2. 检查是否在工作区内
  const workspace = process.cwd();
  if (!normalized.startsWith(workspace)) {
    throw new Error('路径超出工作区范围');
  }
  
  // 3. 检查是否包含危险字符
  if (/[;&|`$()]/.test(userPath)) {
    throw new Error('路径包含非法字符');
  }
  
  // 4. 检查文件扩展名（如果需要）
  const allowedExtensions = ['.txt', '.md', '.json'];
  const ext = path.extname(normalized);
  if (!allowedExtensions.includes(ext)) {
    throw new Error('不支持的文件类型');
  }
  
  return normalized;
}
```

### 用户 ID 验证

```javascript
function validateUserId(userId) {
  // 检查格式（飞书 user_id 通常是字母数字）
  if (!/^[a-zA-Z0-9_-]+$/.test(userId)) {
    throw new Error('无效的用户 ID');
  }
  
  return userId;
}
```

### 数值验证

```javascript
function validateNumber(value, min, max) {
  const num = parseInt(value, 10);
  
  if (isNaN(num)) {
    throw new Error('无效的数字');
  }
  
  if (num < min || num > max) {
    throw new Error(`数字必须在 ${min} 到 ${max} 之间`);
  }
  
  return num;
}
```

## 权限控制

### 检查用户权限

```javascript
async function checkPermission(userId, action) {
  // 从配置或数据库加载权限
  const permissions = await loadUserPermissions(userId);
  
  if (!permissions.includes(action)) {
    throw new Error('权限不足');
  }
}

// 使用示例
if (callback.data.action.value.action === 'delete_file') {
  const userId = callback.data.operator.user_id;
  
  try {
    await checkPermission(userId, 'file.delete');
    // 执行删除操作
  } catch (error) {
    await updateCard(messageId, {
      header: { title: "❌ 权限不足", template: "red" },
      elements: [
        { tag: "div", text: { content: "您没有权限删除文件", tag: "lark_md" } }
      ]
    });
  }
}
```

### 管理员白名单

```javascript
const ADMIN_USERS = [
  'ou_xxx', // 管理员 1
  'ou_yyy'  // 管理员 2
];

function isAdmin(userId) {
  return ADMIN_USERS.includes(userId);
}

// 使用示例
if (callback.data.action.value.action === 'system_restart') {
  if (!isAdmin(callback.data.operator.open_id)) {
    await updateCard(messageId, {
      header: { title: "❌ 权限不足", template: "red" },
      elements: [
        { tag: "div", text: { content: "只有管理员可以重启系统", tag: "lark_md" } }
      ]
    });
    return;
  }
  
  // 执行重启
}
```

## 防止重放攻击

### 使用 event_id 去重

```javascript
const processedEvents = new Set();

function handleCallback(callback) {
  const eventId = callback.data.event_id;
  
  // 检查是否已处理
  if (processedEvents.has(eventId)) {
    console.log('重复事件，跳过');
    return;
  }
  
  // 标记为已处理
  processedEvents.add(eventId);
  
  // 清理旧事件（保留最近 1000 个）
  if (processedEvents.size > 1000) {
    const oldest = Array.from(processedEvents)[0];
    processedEvents.delete(oldest);
  }
  
  // 处理回调
  // ...
}
```

### 时间戳验证

```javascript
function validateTimestamp(timestamp, maxAgeSeconds = 300) {
  const now = Date.now();
  const eventTime = new Date(timestamp).getTime();
  const age = (now - eventTime) / 1000;
  
  if (age > maxAgeSeconds) {
    throw new Error('事件已过期');
  }
  
  if (age < -60) {
    throw new Error('事件时间异常（未来时间）');
  }
}

// 使用示例
try {
  validateTimestamp(callback.timestamp);
  // 处理回调
} catch (error) {
  console.log('时间戳验证失败:', error.message);
  return;
}
```

## 敏感信息保护

### 不要在卡片中显示敏感信息

```javascript
// ❌ 错误：显示完整路径
await updateCard(messageId, {
  elements: [
    { tag: "div", text: { content: `文件路径：/home/user/.ssh/id_rsa`, tag: "lark_md" } }
  ]
});

// ✅ 正确：只显示文件名
const path = require('path');
await updateCard(messageId, {
  elements: [
    { tag: "div", text: { content: `文件名：${path.basename(filePath)}`, tag: "lark_md" } }
  ]
});
```

### 不要在日志中打印敏感信息

```javascript
// ❌ 错误
console.log('用户密码:', password);
console.log('API Token:', token);

// ✅ 正确
console.log('用户密码: [已隐藏]');
console.log('API Token: [已隐藏]');
```

### 使用环境变量存储密钥

```javascript
// ❌ 错误：硬编码
const API_KEY = 'sk_live_xxx';

// ✅ 正确：环境变量
const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  throw new Error('API_KEY 未设置');
}
```

## 错误处理

### 不要泄露内部错误信息

```javascript
// ❌ 错误：暴露内部错误
try {
  await someOperation();
} catch (error) {
  await updateCard(messageId, {
    elements: [
      { tag: "div", text: { content: `错误：${error.stack}`, tag: "lark_md" } }
    ]
  });
}

// ✅ 正确：显示友好的错误信息
try {
  await someOperation();
} catch (error) {
  console.error('内部错误:', error); // 记录到日志
  
  await updateCard(messageId, {
    elements: [
      { tag: "div", text: { content: "操作失败，请稍后重试", tag: "lark_md" } }
    ]
  });
}
```

## 速率限制

### 防止滥用

```javascript
const userRequestCounts = new Map();

function checkRateLimit(userId, maxRequests = 10, windowSeconds = 60) {
  const now = Date.now();
  const userRequests = userRequestCounts.get(userId) || [];
  
  // 清理过期请求
  const validRequests = userRequests.filter(time => now - time < windowSeconds * 1000);
  
  // 检查是否超过限制
  if (validRequests.length >= maxRequests) {
    throw new Error('请求过于频繁，请稍后再试');
  }
  
  // 记录新请求
  validRequests.push(now);
  userRequestCounts.set(userId, validRequests);
}

// 使用示例
try {
  checkRateLimit(callback.data.operator.user_id);
  // 处理回调
} catch (error) {
  await updateCard(messageId, {
    header: { title: "⚠️ 请求过于频繁", template: "orange" },
    elements: [
      { tag: "div", text: { content: error.message, tag: "lark_md" } }
    ]
  });
}
```

## 安全检查清单

在发布技能前，请确保：

- [ ] 所有用户输入都经过验证
- [ ] 没有直接将用户输入传递给 shell 命令
- [ ] 文件路径经过规范化和范围检查
- [ ] 使用目录白名单限制文件访问
- [ ] 文件扩展名经过验证
- [ ] 实现了权限控制
- [ ] 使用 event_id 防止重放攻击
- [ ] 敏感信息不会泄露到卡片或日志
- [ ] 错误信息不会暴露内部实现
- [ ] 实现了速率限制
- [ ] 使用环境变量存储密钥
- [ ] 代码经过安全审计

## 已知漏洞修复历史

### v1.0.2 (2026-02-06)
- **修复**: 任意文件读取漏洞
- **位置**: `scripts/send-card.js` 的 `--template` 参数
- **影响**: 攻击者可以读取系统中的任意文件并发送到飞书
- **修复方案**: 添加目录白名单、文件扩展名验证、JSON 格式验证

### v1.0.1 (2026-02-06)
- **修复**: 命令注入漏洞
- **位置**: `references/gateway-integration.md` 和 `SKILL.md` 的示例代码
- **影响**: 攻击者可以通过文件路径参数执行任意命令
- **修复方案**: 使用 Node.js fs API 替代 shell 命令，添加路径验证

## 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [飞书开放平台安全指南](https://open.feishu.cn/document/home/security-guide)
