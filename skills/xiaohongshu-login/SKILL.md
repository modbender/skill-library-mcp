---
name: xiaohongshu-login
description: 小红书 MCP 登录流程。当用户需要登录小红书、小红书登录过期、或需要获取小红书登录二维码时使用此 skill。
---

# 小红书登录

## 检查登录状态

```bash
mcporter call xiaohongshu-mcp.check_login_status
```

## 获取登录二维码

### Step 1: 调用 MCP 获取二维码

```bash
mcporter call xiaohongshu-mcp.get_login_qrcode --output json
```

**注意**: mcporter 输出的 JSON 格式不标准（属性名无引号），需要用正则提取 base64。

### Step 2: 保存二维码图片

```javascript
// 用 Node.js 提取并保存
const { execSync } = require('child_process');
const fs = require('fs');

const result = execSync('mcporter call xiaohongshu-mcp.get_login_qrcode --output json', { encoding: 'utf8' });

// 正则提取 base64（绕过 JSON 解析问题）
const match = result.match(/data: '([^']+)'/);
if (match) {
  const buffer = Buffer.from(match[1], 'base64');
  fs.writeFileSync('/Users/chen/.openclaw/workspace/xhs_login.png', buffer);
}
```

### Step 3: 显示图片（最可靠）

```bash
# 用 read 工具直接显示图片，确保用户能看到
read /Users/chen/.openclaw/workspace/xhs_login.png
```

### Step 4: 发送给用户

```bash
# 通过飞书发送（备用，可能不稳定）
message action=send channel=feishu filePath=/Users/chen/.openclaw/workspace/xhs_login.png
```

## 完整流程

1. `check_login_status` - 检查是否已登录
2. `get_login_qrcode` - 获取二维码
3. 正则提取 base64 → 保存为 PNG
4. **read 工具显示图片** ← 最重要，确保用户能看到
5. message 发送（可选）

## 常见问题

### 飞书图片不显示
- 本地文件路径在飞书可能不渲染
- 解决：先用 read 工具显示，让用户直接查看

### JSON 解析失败
- mcporter `--output json` 输出格式不标准
- 解决：用正则 `/data: '([^']+)'/` 提取 base64

### 图片不完整
- 可能是 base64 提取不完整
- 解决：确保正则匹配完整，检查文件大小

## 重置登录

```bash
mcporter call xiaohongshu-mcp.delete_cookies
```

删除后需要重新登录。