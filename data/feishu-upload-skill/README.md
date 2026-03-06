# Feishu Upload Skill

![Feishu Logo](https://sf3-cn.feishucdn.com/obj/eden-cn/ljhwzthljh/feishu.png)

一个强大的飞书文件上传技能，允许OpenClaw直接上传文件到飞书云盘并发送到聊天。

## 🚀 快速开始

### 安装
```bash
# 将此文件夹复制到skills目录
cp -r feishu-upload-skill /home/node/.openclaw/workspace/skills/
```

### 基本使用
```bash
# 上传文件并发送到聊天
node feishu_complete_upload.js <文件路径> <聊天ID>

# 示例：上传记忆文件到群聊
node feishu_complete_upload.js memory_files.tar.gz oc_dd899cb1a7846915cdd2d6850bd1dafa
```

## 📦 功能特性

### 核心功能
- **一键上传**：上传本地文件到飞书
- **智能发送**：自动发送文件消息到指定聊天
- **令牌管理**：自动获取和刷新访问令牌
- **大小检查**：自动验证文件大小（≤30MB）
- **格式支持**：支持所有文件类型

### 技术优势
- **零依赖**：使用Node.js 18+原生功能
- **高性能**：直接API调用，无需中间层
- **易集成**：简单命令行接口
- **可扩展**：模块化设计，易于定制

## 🛠️ 使用方法

### 1. 上传并发送文件
```bash
# 上传文本文件
node feishu_complete_upload.js document.txt oc_dd899cb1a7846915cdd2d6850bd1dafa

# 上传图片
node feishu_complete_upload.js photo.jpg oc_dd899cb1a7846915cdd2d6850bd1dafa

# 上传压缩包
node feishu_complete_upload.js archive.zip oc_dd899cb1a7846915cdd2d6850bd1dafa
```

### 2. 仅上传文件（获取文件Key）
```bash
# 上传文件但不发送
node feishu_complete_upload.js file.txt

# 输出示例：
# {
#   "status": "success",
#   "upload": {
#     "file_key": "file_v3_00ur_xxx",
#     "file_name": "file.txt",
#     "file_size": 1234
#   },
#   "sent": false
# }
```

### 3. 手动管理令牌
```bash
# 获取新的访问令牌
./get_feishu_token.sh

# 查看当前令牌
cat feishu_token.txt
```

## 🔧 技术细节

### 工作流程
```
1. 读取配置文件 → 获取App ID/Secret
2. 获取访问令牌 → 调用/auth/v3/tenant_access_token/internal
3. 上传文件 → 调用/im/v1/files (FormData上传)
4. 获取文件Key → 从响应中提取file_key
5. 发送消息 → 调用/im/v1/messages (使用file_key)
6. 返回结果 → 输出JSON格式结果
```

### API调用
```javascript
// 上传文件
POST https://open.feishu.cn/open-apis/im/v1/files
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

// 发送消息
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id
Authorization: Bearer {access_token}
Content-Type: application/json
Body: {"receive_id": "oc_xxx", "msg_type": "file", "content": "{\"file_key\":\"file_v3_xxx\"}"}
```

## 📁 文件结构

```
feishu-upload-skill/
├── SKILL.md              # 技能文档
├── _meta.json           # 元数据
├── README.md            # 说明文件
├── feishu_complete_upload.js    # 主工具（推荐）
├── native_feishu_upload.js      # 简化上传工具
├── get_feishu_token.sh          # 令牌管理脚本
├── feishu_upload_simple.sh      # Bash上传脚本
├── feishu_upload_fixed.sh       # 修复版Bash脚本
└── simple_feishu_upload.js      # 简化版Node.js工具
```

## ⚙️ 配置要求

### 飞书应用权限
- `im:message:send_as_bot` - 发送消息
- 文件上传权限（通过`drive:file:upload`）

### 系统要求
- Node.js ≥ 18.0.0
- OpenClaw ≥ 2026.2.0
- 网络可访问飞书API

### 配置文件
技能会自动读取OpenClaw的配置文件：
- `/home/node/.openclaw/openclaw.json` - 飞书App ID/Secret

## 🐛 故障排除

### 常见问题

**Q: 上传失败，提示权限不足**
A: 检查飞书应用权限配置，确保有`im:message:send_as_bot`权限

**Q: 令牌过期错误**
A: 令牌2小时有效，脚本会自动刷新，或手动运行`./get_feishu_token.sh`

**Q: 文件太大无法上传**
A: 飞书限制单文件≤30MB，请压缩大文件

**Q: 网络连接失败**
A: 检查网络是否能访问`open.feishu.cn`

### 调试模式
```bash
# 启用详细日志
DEBUG=1 node feishu_complete_upload.js file.txt chat_id 2>&1 | tee debug.log
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请：
1. 查看[SKILL.md](SKILL.md)文档
2. 检查故障排除部分
3. 提交GitHub Issue

---

**已成功上传文件示例：**
- ✅ `memory_files.tar.gz` - 记忆文件压缩包
- ✅ `memory_summary.txt` - 记忆摘要文件
- ✅ `test_upload.txt` - 测试文件

**聊天ID:** `oc_dd899cb1a7846915cdd2d6850bd1dafa`