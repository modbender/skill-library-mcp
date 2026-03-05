---
name: "openclaw-newbie-faq"
version: "1.0.43"
displayName: "openclaw新手帮帮忙"
description: "为刚接触 OpenClaw 的新手提供完整指南。安装后请说"启动新手帮助"来启动34567端口的Web服务。源码：https://github.com/kunyashaw/openclaw-newbie-faq.git"
entryPoint:
  type: javascript
  path: "index.js"
triggers:
  keywords: ["启动新手帮助", "停止新手帮助", "openclaw 新手", "openclaw 帮助", "openclaw 指南"]
---

# OpenClaw 新手帮帮忙

## 服务启动说明

安装完本skill之后，因为不会自动启动34567端口；和openclaw对话:'新手帮助',就会启动这个端口

访问地址：http://localhost:34567

## 功能截图

![大模型常识](https://github.com/user-attachments/assets/7b8b7435-4583-4269-b385-4dfe7555a4c7)

![常见问题](https://github.com/user-attachments/assets/ebe867db-5b5c-4fec-93e2-573386e2f7d1)

![命令大全](https://github.com/user-attachments/assets/80a71d51-6332-48a7-b814-aa7096c9e71c)

![调优建议](https://github.com/user-attachments/assets/521f5caf-b7e2-44c6-9840-5eda44704f11)
## 简介

这是一个专为 OpenClaw 新手设计的技能包，提供体系化的学习指南，帮助用户快速上手 OpenClaw。

## 功能特性

### 1. 大模型常识（双视角架构图）

#### 产业视角
展示 AI 大模型行业的上中下游结构：
- **上游**：芯片厂商、云服务商、基础模型公司
- **中游**：AI应用框架、向量数据库、AI中间件
- **下游**：行业应用、企业数字化

#### 工程视角
七层技术架构，从上到下：
- **第7层**：应用产品层 - 把能力变成产品
- **第6层**：Agent与工作流层 - 让模型具备任务执行能力
- **第5层**：能力增强层 - 突破模型原始能力边界
- **第4层**：模型服务层 - 提供稳定可扩展的推理能力
- **第3层**：数据与知识层 - 构建企业级记忆系统
- **第2层**：AI工程与中间件层 - 把AI从实验变成可运营系统
- **第1层**：算力基础设施层 - 物理与资源底座

### 2. 常见问题解答

包含 20 个真实问题，覆盖 7 大分类：
- **安装问题**：command not found、权限错误、Node.js 版本、npm 速度慢
- **网络连接**：无法连接 API、401 错误、429 限流
- **Gateway**：启动失败、立即退出、内存过高
- **频道连接**：Telegram 无法接收、回复慢、多 Bot 配置
- **性能优化**：响应慢、Token 消耗快、CPU 过高
- **配置管理**：config get、config set、config unset
- **频道管理**：channels list、channels add、channels remove备份恢复、切换模型
- **Skill 开发**：安装使用、自定义开发

### 3. 命令大全
- **基础诊断**：status、health、doctor、logs
- **Gateway 管理**：gateway start、gateway stop、gateway restart、gateway status
- **配置管理**：config get、config set、config unset
- **频道管理**：channels list、channels add、channels remove
- **模型管理**：models list、models set
- **Skill 管理**：skills list、skills info、skills check、clawhub search、clawhub install
- **更新升级**：update、--version

### 4. 优化建议

提供 OpenClaw 性能优化和最佳配置方案：
- 调整 Gateway 配置提升响应速度
- 优化 Token 使用降低 API 成本
- 配置缓存提升查询效率
- 模型参数调优建议

## 安装使用

### 安装 Skill

```bash
npx clawhub install openclaw-newbie-faq
```

### 启动 Web 界面

安装完成后，请对 OpenClaw 说"启动新手帮助"，即可自动启动 Web 服务。

或者手动启动：
```bash
cd ~/.openclaw/workspace/skills/openclaw-newbie-faq
node server.js
```

访问地址：http://localhost:34567

### 快速启动脚本

为了方便使用，可以创建一个启动脚本：

```bash
# macOS/Linux
echo '#!/bin/bash
cd ~/.openclaw/workspace/skills/openclaw-newbie-faq
npm start' > ~/start-openclaw-faq.sh
chmod +x ~/start-openclaw-faq.sh

# 使用
~/start-openclaw-faq.sh
```

## 配置说明

- **端口**：默认使用 34567 端口（避免与其他服务冲突）
- **手动启动**：需要手动运行 `npm start` 启动 Web 服务
- **访问地址**：http://localhost:34567

## 使用场景

### 适合人群

- 刚接触 OpenClaw 的新手用户
- 想了解 AI 大模型行业的技术人员
- 需要快速查找 OpenClaw 命令的用户
- 遇到问题需要解决方案的用户

### 使用建议

1. **首次使用**：先浏览"大模型常识"，了解 AI 大模型行业
2. **遇到问题**：查看"常见问题"，找到解决方案
3. **查找命令**：使用"命令大全"，快速找到需要的命令
4. **优化建议**：参考"优化建议"，提升 OpenClaw 性能

## 技术栈

- **前端**：HTML5 + CSS3 + JavaScript
- **后端**：Node.js + HTTP Server
- **端口**：34567
- **无需数据库**：纯静态文件服务
## 反馈与支持

如果您在使用过程中遇到问题或有建议，请：

1. 访问 OpenClaw 官方文档
2. 在 [GitHub](https://github.com/kunyashaw/openclaw-newbie-faq) 上提交 Issue
3. 加入 OpenClaw 社区讨论

## 许可证

MIT License

---

**提示**：安装此 Skill 后，Web 界面会自动在浏览器中打开，您可以随时访问 http://localhost:34567 查看完整指南。
