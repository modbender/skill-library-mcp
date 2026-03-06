---
name: OpenClaw Web Chat Pro
description: 访问 http://localhost:4000
---

# OpenClaw Web Chat Pro

**版本**: 1.0.0  
**作者**: 贝贝  
**描述**: 生产级 AI 聊天网页应用

---

## 安装

```bash
clawhub install webchat-pro
```

## 使用

```bash
cd ~/.openclaw/workspace/skills/webchat-pro
npm install
npm start
```

访问 http://localhost:4000

## 功能

- ✅ 基础聊天（免费）
- ✅ 多模型切换
- ✅ 流式输出
- ✅ 会话持久化
- ✅ 对话导出
- ✅ 深色模式

## Pro 功能（¥9.99/月）

- 📁 文件上传
- 🎤 语音输入/输出
- 🔄 多设备同步
- 👥 团队协作
- 📊 高级统计

## 企业功能（¥99/月）

- 🔒 私有部署
- 🔧 自定义模型
- 🔑 SSO 登录
- 📝 审计日志
- ⚡ SLA 保障

## 配置

编辑 `.env` 文件：

```
PORT=4000
PASSWORD=admin123
ALLOWED_ORIGINS=*
```

## API

- `POST /api/chat` - 发送消息
- `GET /api/models` - 模型列表
- `GET /api/health` - 健康检查

## 支持

文档：https://docs.openclaw.ai  
社区：https://moltbook.com
