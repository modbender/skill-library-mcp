# 🚀 Starter Flow - 启动流

> **新手上路，一键启动——5 个核心技能，3 分钟快速上手 OpenClaw**

**版本：** v1.0.0  
**更新时间：** 2026-02-26 14:00  
**许可证：** MIT

---

## 🎯 这是什么？

Starter Flow 是为 OpenClaw 新手设计的快速启动工具。

**它帮你：**
- 一次性安装 5 个核心技能
- 自主选择想装哪些（不强制）
- 3 分钟内完成安装并开始使用

---

## 🚀 快速开始

### **方法一：交互式安装（推荐）**

```bash
bash ~/.openclaw/workspace/skills/starter-flow/install.sh
```

**显示勾选界面：**
```
╔══════════════════════════════════════════════════════════╗
║  🚀 Starter Flow - 启动流                                 ║
║  5 个核心技能，3 分钟快速上手 OpenClaw                     ║
╚══════════════════════════════════════════════════════════╝

✅ 安全声明：
   • 所有技能本地运行，无云端依赖
   • 用户自主选择，无强制安装
   • 可随时卸载，无残留

请选择要安装的技能（输入数字切换，A 全选，N 全不选，I 安装）：

   [✓] 1. Token 预估 (token-estimator)
       → 预估 Token 消耗，避免超支

   [✓] 2. 智能压缩 (smart-router)
       → 自动压缩内容，节省 60-80% Token

   [✓] 3. 命令全览 (command-flow)
       → 说中文就懂，不用记英文

   [✓] 4. 技能管理 (skill-dashboard)
       → 像管手机 APP 一样简单

   [✓] 5. 用量监控 (token-water-meter)
       → 实时查看 Token 使用情况

语言/Language: [1] 中文  [2] English

输入选项 (1-5/A/N/I/1-2):
```

### **方法二：对话启动**

```
你说："新手启动"

Neo 显示勾选界面，引导安装
```

---

## 📦 包含技能

| 技能 | 用途 | 一句话说明 |
|------|------|-----------|
| **token-estimator** | Token 预估 | 预估消耗，避免超支 |
| **smart-router** | 智能压缩 | 自动压缩，省 60-80% Token |
| **command-flow** | 命令全览 | 说中文就懂，不用记英文 |
| **skill-dashboard** | 技能管理 | 像管手机 APP 一样简单 |
| **token-water-meter** | 用量监控 | 实时查看 Token 用量 |

---

## ⚠️ 安全声明

**本地运行**
- 所有技能本地执行
- 无云端依赖，无隐私泄露

**自主选择**
- 勾选界面，用户自主决定
- 不强制安装，不捆绑销售

**可随时卸载**
```bash
clawhub uninstall 技能名称
```

---

## 📖 安装后引导

**安装完成后，你可以：**

1️⃣ **查看所有命令**
```
你说："斜杠命令"
```

2️⃣ **管理已安装技能**
```
你说："技能控制台"
```

3️⃣ **查看 Token 用量**
```
你说："Token 用量"
```

---

## 🛠️ 故障排查

### **安装失败**

**检查网络：**
```bash
ping clawhub.ai
```

**检查登录：**
```bash
clawhub status
```

**手动安装单个技能：**
```bash
clawhub install token-estimator
clawhub install smart-router
clawhub install command-flow
clawhub install skill-dashboard
clawhub install token-water-meter
```

### **技能无法使用**

**确认已安装：**
```bash
openclaw skills list
```

**重启网关：**
```bash
openclaw gateway restart
```

---

## 📊 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0.0 | 2026-02-26 | Phase 1 首发（交互式脚本） |

---

## 🎯 Phase 2 计划

**即将推出：**
- Web 界面（可视化勾选）
- 中英文切换支持
- 与 ClawHub 深度集成

---

## 🫂 写在最后

**我们设计这个技能，是因为我们知道：**

你第一次用 OpenClaw，不知道从哪开始。

你不想花 1 小时研究装哪些技能。

**所以我们做了这个——**

5 个核心技能，3 分钟快速上手。

**不用选，不用等，一键启动。**

---

*许可证：MIT*  
*开发者：Neo（宇宙神经系统）*  
*链接：https://clawhub.ai/skills/starter-flow*
