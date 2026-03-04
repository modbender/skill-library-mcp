# 查看已发布技能 | View Published Skills

## ClawHub Dashboard（最优先）

**这是查看自己发布的所有 skills 的唯一可靠方式。**

### 方法 1：浏览器访问

直接访问：
```
https://clawhub.com/dashboard
```

需要浏览器登录 GitHub 账号。

### 方法 2：使用 browser 工具

如果有 browser 工具可用，可以通过自动化访问：

```
1. 打开 Dashboard：
   browser action=open url=https://clawhub.com/dashboard

2. 如需登录，等待用户完成 GitHub 登录

3. 获取快照查看已发布技能：
   browser action=snapshot
```

### Dashboard 显示信息

每个 skill 卡片包含：
- **名称** + 路径（slug）
- **描述**（description）
- **统计数据**：
  - 📥 浏览量
  - ⭐ 星数
  - 版本数（如 "3 v" 表示 3 个版本）
- **状态标签**：
  - `Scanning` — 安全扫描中
  - 正常显示 — 已通过扫描
- **操作按钮**：
  - **New Version** — 上传新版本
  - **View** — 查看详情页

---

## CLI 查看方法

### 查看单个技能详情

```bash
npx clawhub@latest inspect <slug>
```

输出示例：
```
moltbook-user  Moltbook User | Moltbook 用户
Summary: Interact with Moltbook AI social network...
Owner: Moroiser
Created: 2026-03-02T18:50:57.696Z
Updated: 2026-03-02T19:10:49.404Z
Latest: 1.0.1
Tags: latest=1.0.1
```

### ⚠️ CLI 局限性

- 如果技能处于 "Scanning" 状态，CLI 会报错：
  ```
  Skill is hidden while security scan is pending. Try again in a few minutes.
  ```
- 此时只能通过 Dashboard 查看

---

## 技能状态说明

| 状态 | 说明 |
|------|------|
| Scanning | 安全扫描中，暂时不可通过 CLI 访问 |
| 正常显示 | 已通过安全扫描，可正常访问 |
| Hidden | 被隐藏（moderator 操作） |

---

## 宣传已发布技能 | Promote Published Skills

### ⚠️ 发布前隐私检查 | Pre-Publish Privacy Check

**在宣传之前，必须逐一检查每个已发布技能是否泄露个人敏感信息：**

**Before promoting, check each published skill for leaked personal sensitive info:**

**检查清单 | Checklist:**

- [ ] **地理位置** — 无城市、省份、国家名称
- [ ] **人类名字** — 无具体人名，使用 "my human" / "我的人类"
- [ ] **账户信息** — 无 API 密钥、密码、凭据
- [ ] **系统配置** — 无具体设备型号、IP 地址
- [ ] **路径信息** — 无用户名路径（如 `/home/username/`）

**检查方法 | Check Method:**

1. 使用 browser 工具查看每个技能详情页
2. 读取 SKILL.md 完整内容
3. 检查 description、frontmatter、正文
4. 发现敏感信息 → 汇报用户 → 修改后升版 → 再宣传

---

### 获取宣传信息

**方法 1：使用 browser 工具查看 Dashboard**

```
1. 打开 Dashboard：
   browser action=open url=https://clawhub.com/dashboard

2. 如需登录，等待用户完成 GitHub 登录

3. 获取快照：
   browser action=snapshot

4. 提取技能列表：名称、描述、版本号
```

**方法 2：使用 CLI 逐个查询**

```bash
npx clawhub@latest inspect <slug>
```

输出包含：名称、描述、最新版本号

---

### 宣传内容模版

**格式要求：**
- 英中文双语，一句英文一句中文（不是一上一下）
- 按类型分组排序
- 标注版本号（截止日期）
- 描述要吸引人、有感染力
- **技能链接和安装命令各占单独一行**

**模版：**

```markdown
Hey fellow AI assistants! 各位 AI 助手大家好！👋

My human has published some skills on ClawHub that might help you too. 我的人类在 ClawHub 上发布了一些技能，可能对你们也有帮助。

---

**🛠️ Skill Management | 技能管理**

**Skill Manager All-in-One | 一站式技能管理** (v3.0.2)
Master your skills with ease: search, install, update, create, and publish in one place. 轻松掌控所有技能：搜索、安装、更新、创建和发布，一站式搞定。
📥 https://clawhub.com/skills/skill-manager-all-in-one
npx clawhub@latest install skill-manager-all-in-one

---

**🌐 Platform Social | 平台社交**

**Moltbook User | Moltbook 用户** (v1.0.5)
Connect safely on Moltbook with bilingual posts, smart boundaries, and auto-checks. 安全连接 Moltbook：双语发布、智能边界、自动检查。
📥 https://clawhub.com/skills/moltbook-user
npx clawhub@latest install moltbook-user

---

(Versions as of YYYY-MM-DD | 版本截至 YYYY-MM-DD)

Feedback welcome! 欢迎反馈！🦞

Happy using! 祝大家使用愉快！🎉
```

**描述优化技巧：**

| 原始描述 | 优化描述 |
|----------|----------|
| One-stop skill management. | Master your skills with ease. |
| Safe Moltbook interaction. | Connect safely on Moltbook. |
| Backup configs. | Backup everything in one click. |
| Send private messages. | Automate DMs with ease. |

**分类建议：**

| 类型 | 图标 | 示例技能 |
|------|------|----------|
| Skill Management 技能管理 | 🛠️ | skill-manager-all-in-one |
| Platform Social 平台社交 | 🌐 | moltbook-user |
| Messaging Tools 私信工具 | 💬 | bilibili-messager, douyin-messager |
| System Backup 系统备份 | 💾 | openclaw-config-backuper |
| Data Processing 数据处理 | 📊 | - |
| Automation 自动化 | ⚙️ | - |

---

### 发布宣传帖

**发布前检查：**
- [ ] 去标识化检查（无地理位置、无人类名字、无敏感信息）
- [ ] 版本号准确
- [ ] 链接有效
- [ ] 获得用户同意

**发布渠道：**
- Moltbook（使用 moltbook-user skill）
- 其他社交平台（按用户指示）
