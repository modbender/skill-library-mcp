# 🌐 OpenClaw Web Chat Pro

**版本**: 1.0.0  
**作者**: 贝贝  
**描述**: 生产级 AI 聊天网页应用，支持多模型切换、流式输出、Token 统计

---

## 🎯 功能特性

### 免费版 (Free)
- ✅ 基础聊天功能
- ✅ 4 个 AI 模型切换
- ✅ 流式输出（打字机效果）
- ✅ 会话持久化
- ✅ 深色模式
- ✅ 对话导出（JSON/Markdown）

### Pro 版 (¥9.99/月)
- ✅ 所有免费版功能
- ✅ 文件上传（图片/PDF/Word）
- ✅ 语音输入/输出
- ✅ 多设备同步
- ✅ 团队协作（共享会话）
- ✅ 高级统计（Token 分析、成本报表）
- ✅ 自定义主题
- ✅ API 访问权限

### 企业版 (¥99/月)
- ✅ 所有 Pro 版功能
- ✅ 私有部署
- ✅ 自定义模型接入
- ✅ SSO 单点登录
- ✅ 审计日志
- ✅ 优先技术支持
- ✅ SLA 保障（99.9% 可用性）

---

## 🚀 快速开始

### 安装
```bash
clawhub install webchat-pro
```

### 配置
```bash
cd ~/.openclaw/workspace/skills/webchat-pro
npm install
cp .env.example .env
# 编辑 .env 配置密码和端口
```

### 启动
```bash
# 开发模式
npm run dev

# 生产模式
npm start

# systemd 服务
sudo systemctl enable openclaw-webchat
sudo systemctl start openclaw-webchat
```

---

## 📁 文件结构

```
webchat-pro/
├── src/
│   ├── server.js          # 后端服务
│   └── public/
│       ├── index.html     # 前端页面
│       └── style.css      # 样式文件
├── docs/
│   ├── README.md          # 本文档
│   ├── API.md             # API 文档
│   └── DEPLOY.md          # 部署指南
├── assets/
│   └── logo.png           # 品牌素材
├── package.json           # 依赖配置
└── README.md              # 技能说明
```

---

## 🔌 API 端点

### 认证
- `POST /api/auth/check` - 验证密码
- `POST /api/auth/password` - 修改密码

### 聊天
- `POST /api/chat` - 发送消息
- `GET /api/history/:id` - 获取历史
- `GET /api/export/:id` - 导出对话

### 模型
- `GET /api/models` - 模型列表
- `POST /api/session/:id/model` - 切换模型

### 系统
- `GET /api/health` - 健康检查
- `GET /api/stats` - 统计信息（Pro）

---

## 💰 定价说明

**免费版**: 永久免费，适合个人用户

**Pro 版**: ¥9.99/月 或 ¥99/年
- 支持 3 个设备
- 10GB 文件存储
- 每月 1000 次 API 调用

**企业版**: ¥99/月 或 ¥999/年
- 无限设备
- 100GB 文件存储
- 无限 API 调用
- 私有部署支持

---

## 📊 技术栈

- **后端**: Node.js + Express + Socket.IO
- **前端**: HTML5 + CSS3 + 原生 JavaScript
- **AI**: OpenClaw Gateway (多模型路由)
- **部署**: systemd + nginx (可选)

---

## 🛡️ 安全特性

- 密码认证（bcrypt 加密）
- 速率限制（60 次/分钟）
- CORS 配置
- 请求体大小限制（10MB）
- 会话隔离
- 日志审计

---

## 📞 支持

- 文档：https://docs.openclaw.ai
- 社区：https://moltbook.com
- 邮箱：support@openclaw.ai

---

## 📝 更新日志

### v1.0.0 (2026-02-22)
- 🎨 全新赛博朋克 UI
- 🌐 Web 特征码标识
- 🔌 Socket.IO 实时通信
- 📊 Token 统计显示
- 💾 对话导出功能
- 🌙 深色模式

---

## 🎯 路线图

### v1.1.0 (2026-03)
- [ ] 文件上传功能
- [ ] Markdown 编辑器

### v1.2.0 (2026-04)
- [ ] 语音输入/输出
- [ ] 多语言支持

### v2.0.0 (2026-06)
- [ ] 团队协作功能
- [ ] API 平台开放

---

**License**: MIT  
**Copyright**: © 2026 OpenClaw Team
