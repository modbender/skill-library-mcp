# OpenClaw 新手帮帮忙

为刚接触 OpenClaw 的新手提供完整指南。

**ClawHub：https://clawhub.ai/kunyashaw/openclaw-newbie-faq**

**源码：https://github.com/kunyashaw/openclaw-newbie-faq.git**

## 功能截图

![大模型常识](https://github.com/user-attachments/assets/7b8b7435-4583-4269-b385-4dfe7555a4c7)

![常见问题](https://github.com/user-attachments/assets/ebe867db-5b5c-4fec-93e2-573386e2f7d1)

![命令大全](https://github.com/user-attachments/assets/80a71d51-6332-48a7-b814-aa7096c9e71c)

![优化建议](https://github.com/user-attachments/assets/521f5caf-b7e2-44c6-9840-5eda44704f11)

## 功能特性

- **大模型常识**：产业视角、工程视角和 OpenClaw 架构的 AI 大模型架构图
- **常见问题**：20 个真实问题解答
- **命令大全**：23 个常用命令
- **优化建议**：性能优化配置

## 安装

```bash
npx clawhub install openclaw-newbie-faq
```

## 使用

安装完成后，对 OpenClaw 说"启动新手帮助"启动 Web 服务。

访问地址：http://localhost:34567

## 快速启动脚本

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

## 许可证

MIT
