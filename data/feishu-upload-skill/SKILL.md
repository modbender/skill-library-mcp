---
name: Feishu Upload Skill
description: 飞书文件上传技能 - 直接上传文件到飞书并发送到聊天
---

# Feishu Upload Skill

飞书文件上传技能 - 直接上传文件到飞书并发送到聊天

## 功能特性

✅ **文件上传**：上传本地文件到飞书云盘
✅ **消息发送**：发送文件消息到指定聊天
✅ **自动令牌管理**：自动获取和刷新访问令牌
✅ **大小限制检查**：自动检查30MB文件大小限制
✅ **多格式支持**：支持各种文件类型（文本、图片、压缩包等）
✅ **纯Node.js实现**：无需额外依赖，使用Node.js 18+原生功能

## 快速开始

### 1. 上传文件并发送到聊天
```bash
node feishu_complete_upload.js <文件路径> <聊天ID>
```

示例：
```bash
node feishu_complete_upload.js document.txt oc_dd899cb1a7846915cdd2d6850bd1dafa
```

### 2. 仅上传文件（获取文件Key）
```bash
node feishu_complete_upload.js <文件路径>
```

### 3. 使用简化脚本
```bash
# 简单上传
node native_feishu_upload.js <文件路径>

# 获取访问令牌
./get_feishu_token.sh
```

## 文件说明

### 核心文件
- `feishu_complete_upload.js` - 完整的上传和发送工具（推荐）
- `native_feishu_upload.js` - 使用原生FormData的简单上传工具
- `get_feishu_token.sh` - 获取和刷新访问令牌的脚本

### 辅助文件
- `feishu_upload_simple.sh` - Bash实现的简单上传脚本
- `feishu_upload_fixed.sh` - 修复版Bash上传脚本
- `simple_feishu_upload.js` - 简化版Node.js上传工具

### 配置文件
- `feishu_token.txt` - 访问令牌缓存文件（自动生成）
- `upload_result.json` - 上次上传的结果文件

## 技术原理

### 三步上传流程
1. **获取访问令牌**：使用App ID和Secret获取`tenant_access_token`
2. **上传文件**：使用飞书`/im/v1/files` API上传文件，获取`file_key`
3. **发送消息**：使用`file_key`发送文件消息到指定聊天

### API端点
- 获取令牌：`POST /open-apis/auth/v3/tenant_access_token/internal`
- 上传文件：`POST /open-apis/im/v1/files`
- 发送消息：`POST /open-apis/im/v1/messages`

### 权限要求
- `im:message:send_as_bot` - 发送消息权限
- `im:file:send_as_bot` - 发送文件权限（可能需要）
- 文件上传权限（通过`drive:file:upload`已授权）

## 使用示例

### 示例1：上传文本文件
```bash
# 创建测试文件
echo "测试内容" > test.txt

# 上传并发送到群聊
node feishu_complete_upload.js test.txt oc_dd899cb1a7846915cdd2d6850bd1dafa
```

### 示例2：上传图片文件
```bash
# 上传图片
node feishu_complete_upload.js photo.jpg oc_dd899cb1a7846915cdd2d6850bd1dafa
```

### 示例3：上传压缩包
```bash
# 压缩文件
tar -czf archive.tar.gz folder/

# 上传压缩包
node feishu_complete_upload.js archive.tar.gz oc_dd899cb1a7846915cdd2d6850bd1dafa
```

## 错误处理

### 常见错误
1. **令牌过期**：自动刷新令牌
2. **文件太大**：超过30MB限制
3. **权限不足**：检查飞书应用权限配置
4. **网络问题**：自动重试机制

### 调试模式
```bash
# 查看详细日志
DEBUG=1 node feishu_complete_upload.js file.txt chat_id
```

## 集成到OpenClaw

### 作为工具调用
```javascript
const { execSync } = require('child_process');
const result = execSync('node feishu_complete_upload.js file.txt chat_id').toString();
console.log(JSON.parse(result));
```

### 作为Skill使用
1. 将此文件夹复制到`skills/`目录
2. 在OpenClaw配置中启用
3. 通过命令或API调用

## 注意事项

1. **文件大小**：最大支持30MB文件
2. **令牌有效期**：访问令牌2小时有效，自动刷新
3. **权限配置**：确保飞书应用有正确的权限
4. **网络环境**：需要能访问飞书API的网络环境
5. **Node.js版本**：需要Node.js 18+（支持全局FormData和fetch）

## 更新日志

### v1.0.0 (2026-02-12)
- ✅ 初始版本发布
- ✅ 完整的文件上传和发送功能
- ✅ 自动令牌管理
- ✅ 错误处理和日志
- ✅ 多文件格式支持

## 许可证

MIT License - 自由使用和修改